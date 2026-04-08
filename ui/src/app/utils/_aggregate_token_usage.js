// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0

export function aggregateTokenUsage(prev, next) {
  const safe = (v) => (typeof v === "number" && !isNaN(v) ? v : 0);
  return {
    input_tokens: safe(prev?.input_tokens) + safe(next?.input_tokens),
    output_tokens: safe(prev?.output_tokens) + safe(next?.output_tokens),
  };
}
