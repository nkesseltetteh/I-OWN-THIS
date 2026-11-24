import asyncio

from livekit import agents
from livekit.plugins import silero

import config
from core import mind
from core.butler import Butler
from core.nudges import nudge_loop
from core.reminders import reminder_loop
from core.session import build_session
from memory import store


def prewarm(proc: agents.JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: agents.JobContext):
    store.init()
    if config.MIND_ENABLED:
        mind.sync_tensions()
    session = build_session(ctx.proc.userdata["vad"])
    recorder = mind.Recorder()
    recorder.attach(session)
    agent = Butler()
    await session.start(room=ctx.room, agent=agent)
    await session.generate_reply(
        instructions=(
            f"Greet {config.OWNER_NAME} in one short line. "
            "If a commitment is overdue or due within a day, mention the most urgent one briefly."
        )
    )
    loops = []
    if config.NUDGES_ENABLED:
        loops.append(asyncio.create_task(nudge_loop(session)))
    if config.REMINDERS_ENABLED:
        loops.append(asyncio.create_task(reminder_loop(session, agent.gate)))
    if config.MIND_ENABLED:
        loops.append(asyncio.create_task(mind.mind_loop()))

    async def stop_loops():
        for task in loops:
            task.cancel()
        await recorder.close()

    ctx.add_shutdown_callback(stop_loops)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
