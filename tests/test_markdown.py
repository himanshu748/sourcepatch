import unittest
from sourcepatch.markdown import parse_markdown, apply_replacements

class MarkdownTests(unittest.TestCase):
    def test_inline_exact_span_and_title_preserved(self):
        text = 'Before [A guide](https://docs.example.org/old "A title") after.\n'
        c = parse_markdown(text)[0]
        self.assertEqual(c.url, 'https://docs.example.org/old')
        self.assertEqual(c.label, 'A guide')
        self.assertEqual(text[c.spans[0].start:c.spans[0].end], c.url)
        self.assertEqual(apply_replacements(text, {c.id: 'https://docs.example.org/new'}), text.replace('/old', '/new'))
    def test_duplicate_destinations_grouped_all_replaced(self):
        text = '[One](https://example.org/a) and [Two](https://example.org/a)'
        cs = parse_markdown(text)
        self.assertEqual(len(cs), 1); self.assertEqual(len(cs[0].spans), 2)
        patched = apply_replacements(text, {cs[0].id: 'https://example.org/b'})
        self.assertEqual(patched, text.replace('/a', '/b'))
        self.assertEqual(apply_replacements(patched, {cs[0].id: 'https://example.org/b'}), patched)
    def test_reference_collapsed_and_shortcut_one_definition(self):
        text = '[One][ DOC ] and [doc][] plus [doc].\n\n[doc]: <https://example.org/a> "Title"\n'
        cs = parse_markdown(text)
        self.assertEqual(len(cs), 1); self.assertEqual(len(cs[0].spans), 1); self.assertEqual(cs[0].occurrences, 3)
        self.assertEqual(apply_replacements(text, {cs[0].id: 'https://example.org/b'}), text.replace('/a', '/b'))
    def test_reference_not_used_excluded(self):
        self.assertEqual(parse_markdown('[unused]: https://example.org/a\n'), [])
    def test_code_images_anchors_and_mail_excluded(self):
        text = '''![alt](https://example.org/image.png)
[local](#heading) [relative](docs/x.md) [mail](mailto:a@example.org)
`[inline](https://example.org/a)`
````md
[inside](https://example.org/b)
```
[still](https://example.org/c)
````
    [indented](https://example.org/d)
[real](https://example.org/real)
'''
        self.assertEqual([c.url for c in parse_markdown(text)], ['https://example.org/real'])
    def test_shared_image_reference_preserved(self):
        self.assertEqual(parse_markdown('[see][shared] ![illustration][shared]\n[shared]: https://example.org/picture\n'), [])
    def test_autolink_and_angle_destination(self):
        self.assertEqual([c.url for c in parse_markdown('<https://example.org/one> [two](<https://example.org/two>)')], ['https://example.org/one', 'https://example.org/two'])
    def test_balanced_parentheses_and_escaped_label(self):
        text = '[A \\] guide](https://example.org/a_(b))'; c=parse_markdown(text)[0]
        self.assertEqual(c.url, 'https://example.org/a_(b)')
        self.assertEqual(apply_replacements(text, {c.id: 'https://example.org/new(x)'}), '[A \\] guide](https://example.org/new%28x%29)')
    def test_html_comment_raw_html_and_escaped_link_excluded(self):
        text='<!-- [a](https://example.org/a) -->\n<script>[b](https://example.org/b)</script>\n\\[c](https://example.org/c)\n[yes](https://example.org/yes)'
        self.assertEqual([c.url for c in parse_markdown(text)], ['https://example.org/yes'])
    def test_malformed_and_nonstring(self):
        self.assertEqual(parse_markdown('[oops](https://example.org/a'), [])
        self.assertEqual(parse_markdown('[oops(https://example.org/a)'), [])
        with self.assertRaises(ValueError): parse_markdown(None)
        with self.assertRaises(ValueError): parse_markdown('x'*200001)
    def test_crlf_unicode_and_no_final_newline_preserved(self):
        text='हेलो\r\n[दस्तावेज](https://example.org/a)';c=parse_markdown(text)[0]
        self.assertEqual(apply_replacements(text,{c.id:'https://example.org/b'}),text.replace('/a','/b'))
    def test_duplicate_reference_definition_first_wins(self):
        self.assertEqual([c.url for c in parse_markdown('[doc]\n[doc]: https://example.org/first\n[doc]: https://example.org/second\n')],['https://example.org/first'])
    def test_image_wrapped_in_link_only_outer_destination(self):
        self.assertEqual([c.url for c in parse_markdown('[![alt](https://example.org/img)](https://example.org/page)')],['https://example.org/page'])
    def test_candidate_markup_chars_encoded(self):
        text='[doc](https://example.org/old)';c=parse_markdown(text)[0]
        self.assertEqual(apply_replacements(text,{c.id:'https://example.org/x)evil('}),'[doc](https://example.org/x%29evil%28)')

class MarkdownSafetyRegressionTests(unittest.TestCase):
    def test_image_angle_destination_and_link_title_not_autolinks(self):
        source='![photo](<https://example.org/image>) [doc](https://example.org/page "see <https://example.org/title>")'
        self.assertEqual([c.url for c in parse_markdown(source)],['https://example.org/page'])
    def test_raw_html_attributes_and_blocks_ignored(self):
        source='<div>\n[hidden](https://example.org/a)\n</div>\n<a href="[hidden](https://example.org/b)">text</a>\n[real](https://example.org/real)'
        self.assertEqual([c.url for c in parse_markdown(source)],['https://example.org/real'])
    def test_reference_with_both_inline_and_image_usage_is_not_rewritten(self):
        source='![image][same] [doc](https://example.org/a) [text][same]\n[same]: <https://example.org/a>\n';c=parse_markdown(source)[0]
        self.assertEqual(apply_replacements(source,{c.id:'https://example.org/b'}),source.replace('[doc](https://example.org/a)','[doc](https://example.org/b)'))

class IndependentReviewRegressionTests(unittest.TestCase):
    def test_nested_link_syntax_inside_autolink_never_overlaps(self):
        source='<https://example.org/[x](https://example.org/inner)>';cs=parse_markdown(source)
        self.assertEqual(len(cs),1);self.assertEqual(cs[0].url,'https://example.org/[x](https://example.org/inner)')
        self.assertEqual(apply_replacements(source,{c.id:'https://example.org/NEW' for c in cs}),'<https://example.org/NEW>')
    def test_nested_image_reference_prevents_shared_definition_rewrite(self):
        source='[![picture][shared]](https://example.org/page) [text][shared]\n[shared]: https://example.org/picture\n';cs=parse_markdown(source)
        self.assertEqual([c.url for c in cs],['https://example.org/page'])
        self.assertEqual(apply_replacements(source,{c.id:'https://example.org/new' for c in cs}),source.replace('/page','/new'))
    def test_list_and_blockquote_fenced_code_stay_untouched(self):
        for source in ['- ```md\n  [example](https://example.org/old)\n  ```\n','> ```md\n> [example](https://example.org/old)\n> ```\n','1. ~~~md\n   [example](https://example.org/old)\n   ~~~\n']:
            with self.subTest(source=source):self.assertEqual(parse_markdown(source),[])

class ParserWorkBoundTests(unittest.TestCase):
    def test_unmatched_and_long_nested_brackets_have_bounded_work(self):
        import sys
        from sourcepatch import markdown
        count=0
        def trace(frame,event,arg):
            nonlocal count
            if event=='line' and frame.f_code.co_filename==markdown.__file__:
                count+=1
                if count>1500000:raise AssertionError('Parser exceeded its bounded-work budget')
            return trace
        for source in ['['*16000,'['*16000+']','[x]('*2000,'<a>'*4000,'<https://example.org/a>'*1500+'['*6000]:
            count=0;sys.settrace(trace)
            try:result=parse_markdown(source)
            finally:sys.settrace(None)
            if source.startswith('<https://'):
                self.assertEqual(len(result),1);self.assertEqual(result[0].occurrences,1500)
            else:self.assertEqual(result,[])

class HTMLBlockRegressionTests(unittest.TestCase):
    def test_unclosed_and_special_raw_html_blocks_are_never_rewritten(self):
        for source in ['<header>\n[example](https://example.org/old)\n','<custom-element>\n[example](https://example.org/old)\n','<![CDATA[\n[example](https://example.org/old)\n]]>','<?instruction\n[example](https://example.org/old)\n?>','<!DOCTYPE\n[example](https://example.org/old)\n>']:
            with self.subTest(source=source):self.assertEqual(parse_markdown(source),[])

if __name__=='__main__':unittest.main()
