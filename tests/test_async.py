# -*- coding: utf-8 -*-
from asyncio import Future, gather, new_event_loop, sleep
from twisted.internet.defer import Deferred, ensureDeferred

from pyee import EventEmitter

def test_asyncio_emit():
    """Test that event_emitters can handle wrapping coroutines as used with
    asyncio.
    """
    loop = new_event_loop()
    ee = EventEmitter(loop=loop)

    should_call = Future(loop=loop)

    @ee.on('event')
    async def event_handler():
        should_call.set_result(True)

    async def create_timeout(loop=loop):
        await sleep(0.1, loop=loop)
        if not should_call.done():
            raise Exception('should_call timed out!')
            return should_call.cancel()

    timeout = create_timeout(loop=loop)

    @should_call.add_done_callback
    def _done(result):
        assert result

    ee.emit('event')

    loop.run_until_complete(gather(should_call, timeout, loop=loop))

    loop.close()


def test_twisted_emit():
    """Test that event_emitters can handle wrapping coroutines when using
    twisted and ensureDeferred.
    """
    ee = EventEmitter(scheduler=ensureDeferred)

    should_call = Deferred()

    @ee.on('event')
    async def event_handler():
        should_call.callback(True)

    @should_call.addCallback
    def _done(result):
        assert result

    @should_call.addErrback
    def _err(exc):
        raise exc

    ee.emit('event')

