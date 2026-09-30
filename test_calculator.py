import unittest
from calculator import calculate_discount_range as calc, convert_discount

def item(id, original, sale):
    return dict(id=id, name=id, original_price=original, sale_price=sale)

class Tests(unittest.TestCase):
    def test_range_and_ties(self):
        r=calc([item('A','1000','790'),item('B','2000','1000'),item('C','100','50')],conditions='會員輸碼')
        self.assertEqual(r['summary']['lowest_zhe'],'5')
        self.assertEqual(r['summary']['highest_zhe'],'7.9')
        self.assertEqual(r['summary']['maximum_percent_off'],'50')
        self.assertEqual(r['summary']['minimum_percent_off'],'21')
        self.assertEqual(r['summary']['best_discount_product_ids'],['B','C'])
        self.assertIn('會員輸碼',r['suggested_copy'][0])
    def test_conservative(self):
        r=calc([item('A','3','2')])['summary']
        self.assertEqual(r['lowest_zhe'],'6.67')
        self.assertEqual(r['maximum_percent_off'],'33.33')
    def test_conversion(self):
        self.assertEqual(convert_discount('8','zhe')['percent_off_conservative'],'20')
        self.assertEqual(convert_discount('21','percent_off')['zhe_conservative'],'7.9')
    def test_no_discount_and_free(self):
        self.assertIn('無折扣',calc([item('A','10','10')])['suggested_copy'][0])
        self.assertIn('0 元',calc([item('A','10','0')])['suggested_copy'][0])
    def test_invalid(self):
        for a,b in [('0','0'),('10','11'),('10','-1'),('NaN','1'),('Infinity','1'),('1,000','5')]:
            with self.assertRaises(ValueError): calc([item('A',a,b)])
        with self.assertRaises(ValueError): calc([])
        with self.assertRaises(ValueError): calc([item('A','10','5'),item('A','10','5')])
    def test_extremes_not_averages(self):
        r=calc([item('A','100','10'),item('B','10000','9000')])['summary']
        self.assertEqual(r['maximum_percent_off'],'90')
        self.assertEqual(r['minimum_percent_off'],'10')

if __name__=='__main__': unittest.main()
