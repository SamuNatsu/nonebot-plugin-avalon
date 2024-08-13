ROUND_SET: dict[int, list[int]] = {
  5: [2, 3, 2, 3, 3],
  6: [2, 3, 4, 3, 4],
  7: [2, 3, 3, 4, 4],
  8: [3, 4, 4, 5, 5],
  9: [3, 4, 4, 5, 5],
  10: [3, 4, 4, 5, 5],
}

ROUND_PROTECT: dict[int, int | None] = {
  5: None,
  6: None,
  7: 4,
  8: 4,
  9: 4,
  10: 4,
}
