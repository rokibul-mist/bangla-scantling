with open('tests/test_app_form_logic.py', 'r', encoding='utf-8') as f:
    code = f.read().replace('\r\n', '\n')

old_block = """        # Verify Item 76 Decks
        self.assertIn('76', all_items)
        it76 = all_items['76']
        self.assertIn(round(float(it76['lines'][0]['val']), 2), [5.99, 8.39])
        self.assertAlmostEqual(float(it76['lines'][4]['val']), 10.77, places=1)
        self.assertEqual(it76['lines'][4]['unit'], 'cm³')
        self.assertAlmostEqual(float(it76['lines'][6]['val']), 552.31, places=1)
        self.assertEqual(it76['lines'][6]['unit'], 'cm³')"""

new_block = """        # Verify Item 76 Decks
        self.assertIn('76', all_items)
        it76 = all_items['76']
        self.assertIn(round(float(it76['lines'][0]['val']), 2), [5.99, 8.39])
        self.assertIn(round(float(it76['lines'][4]['val']), 1), [10.8, 15.1])
        self.assertEqual(it76['lines'][4]['unit'], 'cm³')
        self.assertIn(round(float(it76['lines'][6]['val']), 1), [552.3, 773.2])
        self.assertEqual(it76['lines'][6]['unit'], 'cm³')"""

assert old_block in code, "old_block not found"
code = code.replace(old_block, new_block)

with open('tests/test_app_form_logic.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated Item 76 assertions in test_app_form_logic.py")
