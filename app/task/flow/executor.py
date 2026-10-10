from dataclasses import asdict

from app.domain.state import DialogueState
from app.task.flow.flows import FlowsList
from app.task.action.runner import ActionRunner, ActionCall, ActionResult
from app.domain.messages import BotMessage
from app.task.flow.steps import FlowStep, StartedFlowStep, CollectedFlowStep, ActionFlowStep, EndFlowStep
from app.task.flow.links import FlowStepStaticLink, FlowStepConditionalLink, FlowStepFallbackLink
from app.domain.contexts import CollectedSystemContext


class FlowExecutor:
    """
    流程执行器：推进yaml中定义的业务任务流程以及系统任务流程
    """

    async def run_task(self,
                       state: DialogueState,
                       flows: FlowsList,
                       action_runner: ActionRunner
                       ):
        """
        推进yaml中定义的业务任务流程以及系统任务流程
        :param state:
        :param flows:
        :param action_runner:
        :return:
        """
        final_messages: list[BotMessage] = []
        while True:  # 找要执行的流程步骤

            # 1. 推进流程（以及内部step）type:类型是action(行动)【action_listen action_response action_xxx】
            action_call: ActionCall = self._advance_until_action(state, flows)

            if action_call.action_name == "action_listen":
                break
            else:
                action_result: ActionResult = await action_runner.run(action_call, state)
                state.set_slots(action_result.slot_updates)
                final_messages.extend(action_result.messages)

        return final_messages

    def _advance_until_action(self,
                              state: DialogueState,
                              flows: FlowsList) -> ActionCall:
        """
        流程推进的核心
        :param state:
        :param flows:
        :return:
        """

        while True:

            # 1. 获取当前时刻的上下文（系统任务流程的上下文以及业务任务流程的上下文）
            current_active_task = state.current_active_task()  # current_active_task:动态改变的（在不同的时刻获取不同的任务流程）

            if current_active_task is None:
                return ActionCall(action_name="action_listen")



            # 2. 获取上下文中的流程Id
            flow_id = current_active_task.flow_id

            # 3. 获取上下文中的流程对象
            flow = flows.get_flow_by_id(flow_id)

            # 4. 获取上下文中的流程对象对应step
            step = flow.get_step_by_id(current_active_task.step_id)

            # 5. 运行当前step
            action_call: ActionCall | None = self._run_step(state, step, flows)

            # 6. 如果step的类型是action,退出while true ,否则就可以继续往下推
            if action_call is not None:
                return action_call

    def _run_step(self, state: DialogueState,
                  step: FlowStep,
                  flows: FlowsList) -> ActionCall | None:
        """
        运行每一个step
        :param state:
        :param step:
        :param flows:
        :return:
        """
        if isinstance(step, StartedFlowStep):
            return self._run_start_step(step, state)
        if isinstance(step, CollectedFlowStep):
            return self._run_collect_slots_step(step, state, flows)
        if isinstance(step, EndFlowStep):
            return self._run_end_step(state)
        if isinstance(step, ActionFlowStep):
            return self._run_action_step(step, state)

    def _run_start_step(self, step: StartedFlowStep,
                        state: DialogueState) -> None:

        # 1. 推进下一步
        self._advance_next_step(state, step)
        # 2. 返回None
        return None

    def _advance_next_step(self, state, step):
        # 1. 寻找下一个step边
        next_step_id = self._select_next_step(step, state)
        # 2. 更新当前任务上下文的step_id(给当前执行任务流程的上下文用)不做这个动作，出不来
        state.current_active_task().step_id = next_step_id

    def _select_next_step(self,
                          step: FlowStep,
                          state: DialogueState
                          ) -> str:

        for link in step.next:
            if isinstance(link, FlowStepStaticLink):
                return link.target  # 下一个边的ID
            if isinstance(link, FlowStepConditionalLink):
                if self._eval_condition(state, link.condition):
                    return link.target
            if isinstance(link, FlowStepFallbackLink):
                return link.target
        return "step not exist next"

    def _eval_condition(self,
                        state: DialogueState,
                        condition: str
                        ) -> bool:
        data = {
            "slots": state.active_task.slots,
            "context": asdict(state.current_active_task())
        }
        return bool(eval(condition, {}, data))

    def _run_end_step(self, state: DialogueState) -> None:
        """
        1. 清空state中系统任务流程上下文
        2. 清空state中业务任务流程上下文
        :param state:
        :return:
        """
        if state.active_system_task:
            state.end_active_system_task()
        else:
            state.end_active_task()
        return None

    def _run_action_step(self,
                         step: ActionFlowStep,
                         state: DialogueState) -> ActionCall:

        self._advance_next_step(state, step)

        return self._build_action_call(state, step)

    def _build_action_call(self, state, step) -> ActionCall:
        # 1. 获取action_name (action_listen/action_response/action_xxx)
        # 2. 获取action_kwargs (构建参数)
        action_name = step.action
        action_kwargs = step.args
        # action_kwargs有可能有:结构有可能是一个str、dict{}  有可能没有:结构是个空字典{}
        if isinstance(action_kwargs, str):
            # "context.response" :response  {}
            action_kwargs = asdict(state.active_system_task)[action_kwargs.split(".")[1]]
        return ActionCall(action_name=action_name, action_kwargs=action_kwargs)

    def _run_collect_slots_step(self,
                                step: CollectedFlowStep,
                                state: DialogueState,
                                flows: FlowsList):


        # 1. 判断槽位是否已经填过
        if state.active_task.slots.get(step.slot_name):
            if step.validate:
                if self._eval_condition(state, step.validate.condition):
                    self._advance_next_step(state, step)
                    return None
                else:
                    state.remove_slot(step.slot_name)
                    if step.validate.failure_response:
                        return ActionCall(action_name="action_response",
                                          action_kwargs=asdict(step.validate.failure_response))
                    else:
                        return ActionCall(action_name="action_response",
                                          action_kwargs={"text": "您填写的信息有误，请你重新在填"})
            else:
                self._advance_next_step(state, step)
                return None
        else:
            state.start_active_system_task(CollectedSystemContext(
                flow_id="system_collect_information",
                step_id=flows.get_flow_by_id('system_collect_information').start_step().id,
                slot_name=step.slot_name,
                response=asdict(step.response)
            ))
            return None




if __name__ == '__main__':
    condition = "context.get('reason') == 'clarification_rejected'"
    data = {
        "context": {"reason": "abc"}
    }

    print(bool(eval(condition, {}, data)))
