import { describe, it, expect } from 'vitest';
import { destinationError } from './publication';

describe('publication destination', () => {
  const check = (name: string) => destinationError(name, 'example', 'https://github.com/example/fixture');
  it.each(['fixture-fixed', 'My-custom_fix.2026'])('accepts %s', name => {
    expect(check(name)).toBe('');
  });
  it.each(['', '.', '..', '...', 'repo.git', 'repo.GIT', 'a/b', 'a b', 'x\n', 'x'.repeat(101), 'Fixture'])('rejects %s', name => {
    expect(check(name)).not.toBe('');
  });
});
