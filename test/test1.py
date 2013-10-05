import io
import sys

import unittest

import monitoring

class monitoringTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pretty_print(self):
        with open('test/input1', 'rb') as f_in1,\
                open('test/hum_read_output1', 'r') as f_out1,\
                open('test/input2', 'rb') as f_in2,\
                open('test/hum_read_output2', 'r') as f_out2:
            self.testdata_in1 = f_in1.read()
            self.testdata_out1 = f_out1.read()
            self.testdata_in2 = f_in2.read()
            self.testdata_out2 = f_out2.read()
        self.assertTrue(monitoring.pretty_print(self.testdata_in1), self.testdata_out1[:-1])
        self.assertMultiLineEqual(monitoring.pretty_print(self.testdata_in1), self.testdata_out1)
        self.assertMultiLineEqual(monitoring.pretty_print(self.testdata_in2), self.testdata_out2)

    def test_mg_read(self):
        s = b'test'
        stream = io.BytesIO(s)
        stream.inWaiting = lambda : len(s)-stream.tell()
        ser = stream
        self.assertTrue(monitoring.Ser(stream).mg_read() == s)

    def test_mg_write(self):
        pass

    @unittest.skip("time")
    def test_opros1(self):
        s = b'test'
        stream = io.BytesIO(s)
        stream.inWaiting = lambda : 0
        ser = stream
        x = sys.stdout
        sys.stdout = None
        monitoring.Ser(stream).opros1(1)
        sys.stdout = x
        self.assertTrue(True)

    @unittest.skip("time")
    def test_opros2(self):
        s = b'test'
        stream = io.BytesIO(s)
        stream.inWaiting = lambda : 0
        ser = stream
        x = sys.stdout
        sys.stdout = None
        monitoring.Ser(stream).opros2(1)
        sys.stdout = x
        self.assertTrue(True)

    def test_get_filename_date(self):
        self.assertRegex(monitoring.get_filename_data('test/today.txt'),
            "test/today_\d{6}.txt")

    def test_rename_file(self):
        self.assertRegex(monitoring.rename_file('test/today.txt'),
            "test/today_\d{6}.txt")

    def test_namemgsGen(self):
        self.assertMultiLineEqual(''.join(
            (monitoring.name_mgs_gen(monitoring.MGSGN)) )[:-1],
            "\$D|\$B|\$9|\$7|\$5|\$3|\$1")

    def test_write_sideGn(self):
        with open('test/input1', 'rb') as f_in1, \
                open('test/hum_read_output_result1', 'r') as f_out1:
            self.testdata_in1 = f_in1.read()
            self.testdata_out1 = f_out1.read()
        self.assertMultiLineEqual(
            monitoring.write_sideGn(self.testdata_in1, monitoring.PATTERNGN),
            self.testdata_out1)

    def test_write_sideAn(self):
        with open('test/input2', 'rb') as f_in2, \
               open('test/hum_read_output_result2', 'r') as f_out2:
            self.testdata_in2 = f_in2.read()
            self.testdata_out2 = f_out2.read()
        print(len(monitoring.write_sideAn(self.testdata_in2, monitoring.PATTERNAN)))
        print(len(self.testdata_out2))
        self.assertMultiLineEqual(
            monitoring.write_sideAn(self.testdata_in2, monitoring.PATTERNAN),
            self.testdata_out2)


if __name__ == '__main__':
    unittest.main()
