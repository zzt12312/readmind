function escapeHtml(input: string) {
  return input
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

export function highlightText(input: string, keyword: string) {
  const safe = escapeHtml(input)
  const trimmed = keyword.trim()
  if (!trimmed) return safe

  const escapedKeyword = trimmed.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const matcher = new RegExp(`(${escapedKeyword})`, 'gi')
  return safe.replace(matcher, '<mark>$1</mark>')
}
