# A field guide to reliable data scripts

A practical reading list for a small research team. Some links in this
**authored fixture** are deliberately out of date; no live claims are made.

## Files that survive a refactor

Use [Python pathlib](https://docs.python.org/3/library/pathlib-old.html)
for readable filesystem operations. Keep the [pathlib quick reference](https://docs.python.org/3/library/pathlib-old.html)
close while you migrate scripts.

## Requests that can be cancelled

Read [Abort a fetch request][abort] before wiring a cancel button.
Two similarly named pages may help; decide which actually fits this sentence.

## Tables and typed records

Keep [pandas DataFrame](https://pandas.pydata.org/docs/old/reference/frame.html)
and [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
as your starting points.

The [private team dashboard](http://127.0.0.1:8080/metrics) is out of scope.

[abort]: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/abort-old "Cancellation"

```python
# Examples are never rewritten: [sample](https://example.org/code)
```

![Diagram stays untouched](https://example.org/diagram.png)
