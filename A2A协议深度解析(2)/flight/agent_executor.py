import uuid

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (Part, Task, TextPart, UnsupportedOperationError, TaskArtifactUpdateEvent, Artifact)
from a2a.utils import new_task
from a2a.utils.errors import ServerError


class FlightAgentExecutor(AgentExecutor):

    async def execute(
            self,
            context: RequestContext,
            event_queue: EventQueue,
    ) -> None:
        task = context.current_task
        if not task:
            task = new_task(context.message)
            # 修复：await
            await event_queue.enqueue_event(task)
        # 修复：contextId → context_id
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        artifact_id = str(uuid.uuid4())

        # 修复：全部加 await
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                taskId=task.id,
                contextId=task.context_id,  # 修复
                artifact=Artifact(
                    artifactId=artifact_id,
                    parts=[Part(root=TextPart(text="你要查询的机票"))],
                ),
                append=False,
                lastChunk=False
            )
        )
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                taskId=task.id,
                contextId=task.context_id,  # 修复
                artifact=Artifact(
                    artifactId=artifact_id,
                    parts=[Part(root=TextPart(text="如下："))],
                ),
                append=True,
                lastChunk=False
            )
        )
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                taskId=task.id,
                contextId=task.context_id,  # 修复
                artifact=Artifact(
                    artifactId=artifact_id,
                    parts=[Part(root=TextPart(
                        text="1. 航班号 FAKE-001，起飞时间 20:00，余票 30 张；2. 航班号 FAKE-002，起飞时间 23:00，余票 50 张"))],
                ),
                append=True,
                lastChunk=True
            )
        )
        # 修复：await
        await updater.complete()

    async def cancel(
            self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())