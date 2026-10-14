export function destinationError(name: string, owner: string, source: string): string {
  if (!/^[A-Za-z0-9_.-]{1,100}$/.test(name) || /^\.+$/.test(name) || name.toLowerCase().endsWith('.git')) {
    return 'Use 1–100 letters, numbers, dots, underscores or hyphens. The name cannot be only dots or end with .git.';
  }
  if (`https://github.com/${owner}/${name}`.toLowerCase() === source.toLowerCase()) {
    return 'Choose a new repository name, different from the source repository.';
  }
  return '';
}
