import { describe, it, expect } from 'vitest';
import { decodeSSE } from './api';
describe('SSE framing',()=>{
  it('retains partial frames and ignores heartbeats',()=>{
    const data=': heartbeat\n\nid: 1\ndata: {"event_id":1}\n\nid: 2\ndata: {"event_id":';
    const first=decodeSSE(data);
    expect(first.events.map(e=>e.event_id)).toEqual([1]);
    expect(decodeSSE(first.remainder+'2}\n\n').events.map(e=>e.event_id)).toEqual([2]);
  });
});
