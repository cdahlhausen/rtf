from django.test import TestCase
from rtfapp.managers import SHPManager
import openpyxl
import shapefile
import os
import zipfile, shutil
from os import path

def create_shp_file_point(shp_path):
    w = shapefile.Writer(shapefile.POINT)
    w.point(1,1)
    w.point(3,1)
    w.point(4,3)
    w.point(2,2)
    w.point(5,5)
    w.field('PROP_ID')
    w.field('OWNER')
    w.field('ADDRESS')
    w.field('ZIPCODE')
    w.record('1', 'TEST1', '123 TEST ST', '12345')
    w.record('2', 'TEST2', '223 TEST ST', '22345')
    w.record('3', 'TEST3', '323 TEST ST', '32345')
    w.record('4', 'TEST4', '423 TEST ST', '42345')
    w.record('5', 'TEST5', '523 TEST ST', '52345')
    w.save(shp_path)

def create_shp_file_area(shp_path, pin_name):
    w = shapefile.Writer(shapefile.POLYGON)
    w.poly(shapeType=3, parts=[[[0,0],[0,1],[1,1],[1,0],[0,0]]])
    w.poly(shapeType=3, parts=[[[1,1],[1,2],[2,2],[2,1],[1,1]]])
    w.poly(shapeType=3, parts=[[[2,2],[2,3],[3,3],[3,2],[2,2]]])
    w.poly(shapeType=3, parts=[[[3,3],[3,4],[4,4],[4,3],[3,3]]])
    w.poly(shapeType=3, parts=[[[4,4],[4,5],[5,5],[5,4],[4,4]]])
    w.field(pin_name)
    w.record('1')
    w.record('2')
    w.record('3')
    w.record('4')
    w.record('5')
    w.save(shp_path)

def create_xlsx_file(xlsx_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([0,0,0,0,0,0,0,0,0,0,0,0])
    ws.append([0,1,0,0,'Bob',0,0,0,'123 Fake Ln',0,'Cville','22903'])
    ws.append([0,2,0,0,'Jane',0,0,0,'nL ekaF 321',0,None,'30922'])
    ws.append([0,3,0,0,'Kyle',0,0,0,'123 Test St',0,None,'10922'])
    ws.append([0,4,0,0,'Michael',0,0,0,'420 Noscope Dr',0,None,'40922'])
    ws.append([0,5,0,0,'John',0,0,0,'5354 Hi St',0,None,'20922'])
    wb.save(xlsx_path)

class SHPManagerTests(TestCase):
    """Test cases for the SHPManager"""
 
    def test_getShpFileName_no_prefix(self):
        l1 = ['test.shp', 'test.dbx', 'test.xml']
        l2 = ['test.txt']
        t1 = SHPManager.getShpFileName(l1)
        t2 = SHPManager.getShpFileName(l2)
        self.assertEqual(t1, 'test.shp')
        self.assertEqual(t2, '')   

    def test_getShpFileName_with_prefix(self):
        l3 = ['parcels_current.shp', 'test.shp', 'parcelsStacked_current.shp']
        t3 = SHPManager.getShpFileName(l3, prefix='Stacked_current')
        self.assertEqual(t3, 'parcelsStacked_current.shp')

    def test_getShpFileName_empty(self):
        l1 = []
        t1 = SHPManager.getShpFileName(l1)
        self.assertEqual(t1, '')  

    def test_getExcelFileName_empty(self):
        l1 = []
        t1 = SHPManager.getExcelFileName(l1)
        self.assertEqual(t1, '')


    def test_getExcelFileName_noXlsx(self):
        l2 = ['a.xls', 'b.doc']
        t2 = SHPManager.getExcelFileName(l2)
        self.assertEqual(t2, '')


    def test_getExcelFileName_hasXlsx(self):
        l3 = ['a.xls', 'b.doc', 'c.xlsx']
        t3 = SHPManager.getExcelFileName(l3)
        self.assertEqual(t3, 'c.xlsx')


    def test_getParcelsFromExcel_notExist(self):
        path = ''

        result = SHPManager.getParcelsFromExcel(path)        

        self.assertEqual(len(result), 0)


    def test_getParcelsFromExcel_notXlsx(self):
        testFile = open('test.txt', 'w')
        testFile.close()

        result = SHPManager.getParcelsFromExcel('test.txt')
        self.assertEqual(len(result), 0)
        os.remove('test.txt')


    def test_getParcelsFromExcel(self):
        filename = path.expanduser("~") + "/files/test_excel.xlsx"
        create_xlsx_file(filename)

        parcels = SHPManager.getParcelsFromExcel(filename)

        self.assertEqual(len(parcels), 5)
        self.assertEqual(parcels[1].owner, 'Bob')
        self.assertEqual(parcels[1].id, 1)
        self.assertEqual(parcels[1].address, "123 Fake Ln, Cville, 22903")
        self.assertEqual(parcels[2].owner, 'Jane')
        self.assertEqual(parcels[2].id, 2)
        self.assertEqual(parcels[2].address, "nL ekaF 321, 30922")
        os.remove(filename)   

    def test_distance(self):
        ''' Tests that the distance formula works Pythagorean Triangle '''
        self.assertEqual(5.0, SHPManager.distance(3, 10, 6, 14))

    def test_getMidpoint(self):
        ''' Tests that the midpoint between two points is calculated correctly '''
        self.assertEqual((2, 3), SHPManager.getMidpoint(1, 2, 3, 4))

    def test_getRecordsAndFields_point(self):
        filename = path.expanduser("~") + "/files/test_point_shpfile.shp"
        create_shp_file_point(filename)
        test_rf = SHPManager.getRecordsAndFields(filename, 'point')
        self.assertEqual(len(test_rf[0]), 5)
        self.assertEqual(len(test_rf[1]), 4)
        self.assertEqual(test_rf[1][0][0], 'PROP_ID')
        os.remove(filename)
        os.remove(filename[:-3]+'dbf')
        os.remove(filename[:-3]+'shx')

    def test_getRecordsAndFields_area(self):
        filename = path.expanduser("~") + "/files/test_area_shpfile.shp"
        create_shp_file_area(filename, 'PIN')
        test_rf = SHPManager.getRecordsAndFields(filename, 'area')
        self.assertEqual(len(test_rf[0]), 5)
        self.assertEqual(len(test_rf[1]), 1)
        self.assertEqual(test_rf[1][0][0], 'PIN')
        os.remove(filename)
        os.remove(filename[:-3]+'dbf')
        os.remove(filename[:-3]+'shx')

    def test_parseCityParcels_with_records(self):
        p_filename = path.expanduser("~") + "/files/test_point_shpfile.shp"
        create_shp_file_point(p_filename)
        a_filename = path.expanduser("~") + "/files/test_area_shpfile.shp"
        create_shp_file_area(a_filename, 'PIN')
        test_point_rf = SHPManager.getRecordsAndFields(p_filename, 'point')
        test_area_rf = SHPManager.getRecordsAndFields(a_filename, 'area')        
        result = SHPManager.parseCityParcels(test_point_rf, test_area_rf)
        self.assertEqual(len(result), 5)
        self.assertEqual(len(result), 5)
        os.remove(p_filename)
        os.remove(p_filename[:-3]+'dbf')
        os.remove(p_filename[:-3]+'shx')
        os.remove(a_filename)
        os.remove(a_filename[:-3]+'dbf')
        os.remove(a_filename[:-3]+'shx')

    def test_getCountyParcels(self):
        a_filename = path.expanduser("~") + "/files/test_Stacked_current.shp"
        create_shp_file_area(a_filename, 'GPIN')
        e_filename = path.expanduser("~") + "/files/test_excel.xlsx"
        create_xlsx_file(e_filename)
        areaFiles = [a_filename, a_filename[:-3]+'dbf', a_filename[:-3]+'shx']
        excelFiles = [e_filename]

        parcels = SHPManager.getCountyParcels(areaFiles, excelFiles)
        self.assertEqual(len(parcels), 5)

        os.remove(e_filename)
        os.remove(a_filename)
        os.remove(a_filename[:-3]+'dbf')
        os.remove(a_filename[:-3]+'shx')

    def test_getParcels_files_exist(self):
        p_filename = path.expanduser("~") + "/files/test_point_shpfile.shp"
        create_shp_file_point(p_filename)
        a_filename = path.expanduser("~") + "/files/test_area_shpfile.shp"
        create_shp_file_area(a_filename, 'PIN')
        areaFiles = [a_filename, a_filename[:-3]+'dbf', a_filename[:-3]+'shx']
        pointFiles = [p_filename, p_filename[:-3]+'dbf', p_filename[:-3]+'shx']
        parcels = SHPManager.getParcels(pointFiles, areaFiles)
        self.assertEqual(len(parcels), 5)
        os.remove(p_filename)
        os.remove(p_filename[:-3]+'dbf')
        os.remove(p_filename[:-3]+'shx')
        os.remove(a_filename)
        os.remove(a_filename[:-3]+'dbf')
        os.remove(a_filename[:-3]+'shx')

    def test_getParcels_files_not_exist(self):
        a_filename = path.expanduser("~") + "/files/test_area_shpfile.shp"
        p_filename = path.expanduser("~") + "/files/test_point_shpfile.shp"
        areaFiles = [a_filename, a_filename[:-3]+'dbf', a_filename[:-3]+'shx']
        pointFiles = [p_filename, p_filename[:-3]+'dbf', p_filename[:-3]+'shx']
        parcels = SHPManager.getParcels(pointFiles, areaFiles)
        self.assertEqual(len(parcels), 0)

    def test_parseParcels_no_records(self):
        pointRF = [[],[]]
        areaRF = [[],[]]
        t1 = SHPManager.parseCityParcels(pointRF, areaRF)
        #t2 = SHPManager.parseParcels(pointRF, areaRF)
        self.assertEqual(len(t1), 0)
        #self.assertEqual(len(t2), 0)

    def test_getIntersections(self):
        line_segment = ''
        first_point = ''
        parcels = []
        intersections = SHPManager.getIntersections(line_segment, first_point, parcels)

        self.assertEqual(len(intersections), 0)

    def test_atomize_placemark(self):
        placemark = ''
        parcels = []
        self.assertEqual(0,0)

    def test_intersect_parcel(self):
        segment = ''
        parcels = []
        full_possible_parcels = []
        placemark_segments = []
        self.assertEqual(0,0)


