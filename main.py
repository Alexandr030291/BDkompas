# -*- coding: utf-8 -*-

import pythoncom
from win32com.client import Dispatch, gencache
import LDefin2D
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import random
import sqlite3


class KompasAPI:
    const, const_3d = None, None
    module5, api5 = None, None
    module7, api7 = None, None

    @staticmethod
    def get_const():
        const = gencache.EnsureModule("{75C9F5D0-B5B8-4526-8681-9903C567D2ED}", 0, 1, 0).constants
        const_3d = gencache.EnsureModule("{2CAF168C-7961-4B90-9DA2-701419BEEFE3}", 0, 1, 0).constants
        return const, const_3d

    @staticmethod
    def get_api7():
        module = gencache.EnsureModule("{69AC2981-37C0-4379-84FD-5DD2F3C0A520}", 0, 1, 0)
        api = module.IKompasAPIObject(
            Dispatch("Kompas.Application.7")._oleobj_.QueryInterface(module.IKompasAPIObject.CLSID,
                                                                     pythoncom.IID_IDispatch))
        return module, api

    @staticmethod
    def get_api5():
        module = gencache.EnsureModule("{0422828C-F174-495E-AC5D-D31014DBBE87}", 0, 1, 0)
        api = module.KompasObject(
            Dispatch("Kompas.Application.5")._oleobj_.QueryInterface(
                module.KompasObject.CLSID, pythoncom.IID_IDispatch))
        return module, api


    # Посчитаем количество листов каждого из формата
    @staticmethod
    def amount_sheet(doc7):
        sheets = {"A0": 0, "A1": 0, "A2": 0, "A3": 0, "A4": 0, "A5": 0}
        for sheet in range(doc7.LayoutSheets.Count):
            format = doc7.LayoutSheets.Item(sheet).Format  # sheet - номер листа, отсчёт начинается от 0
            sheets["A" + str(format.Format)] += 1 * format.FormatMultiplicity
        return sheets

    @classmethod
    def open(cls, fname):
        doc7 = cls.api7.Application.Documents.Open(fname, Visible=True, ReadOnly=True)
        if not doc7:
            return None
        #cls.api7.Application.HideMessage = cls.const.ksHideMessageNo  # Отвечаем НЕТ на любые вопросы программы
        return doc7

    @classmethod
    def close(cls, doc7):
        if doc7 is None: return
        doc7.Close(cls.const.kdDoNotSaveChanges)

    """
    @staticmethod
    def get_path_doc(obj):
        РАСШИРЕНИЯ = [".spw", ".cdw"]
        файлы = obj.get("файлы")
        for файл in файлы:
            if os.path.splitext(файл)[1] in РАСШИРЕНИЯ:
                return файл
        return None
    """

KompasAPI.module7, KompasAPI.api7 = KompasAPI.get_api7()
KompasAPI.module5, KompasAPI.api5 = KompasAPI.get_api5()
KompasAPI.const, KompasAPI.const_3d = KompasAPI.get_const()


class KompasDoc:
    def __init__(self, fname):
        self.doc7 = KompasAPI.open(fname)
        self.doc5 = None
        if self.doc7 is not None:
            self.doc5 = KompasAPI.api5.SpcActiveDocument()

    def __del__(self):
        if self.doc7 is not None:
            KompasAPI.close(self.doc7)

    def get_info(self):
        result = {}
        stamp = self.doc7.LayoutSheets.Item(0).Stamp
        result[Database.KEYS_DOC[0]] = stamp.Text(2).Str
        result[Database.KEYS_DOC[1]] = stamp.Text(1).Str
        result[Database.KEYS_DOC[2]] = stamp.Text(3).Str
        result[Database.KEYS_DOC[3]] = KompasAPI.amount_sheet(self.doc7)
        return result

    def get_spc(self):
        if self.doc5 is None:
            return None
        iIter = KompasAPI.api5.GetIterator()  # Получить интерфейс итератора
        iIter.ksCreateSpcIterator("graphic.lyt", 1, 0)  # Создать итератор по объектам спецификации
        obj = iIter.ksMoveIterator("F")  # чтение первой строки

        result = {
            # "Документация":[],
            # "Сборочные единицы":[],
            # "Детали":[],
            # "Стандартные изделия":[],
            # "Прочие изделия":[],
            # "Материалы":[]
        }
        while (obj):
            iSpc = self.doc5.GetSpecification()
            раздел = iSpc.ksGetSpcSectionName(obj)

            iSpcObjParam = KompasAPI.module5.ksSpcObjParam(KompasAPI.api5.GetParamStruct(KompasAPI.const.ko_SpcObjParam))
            self.doc5.ksGetObjParam(obj, iSpcObjParam, LDefin2D.ALLPARAM)
            DynamicArray = iSpcObjParam.GetDocArr()
            обозначение = iSpc.ksGetSpcObjectColumnText(obj, 4, 1, 0)
            наименование = iSpc.ksGetSpcObjectColumnText(obj, 5, 1, 0)
            количество = iSpc.ksGetSpcObjectColumnText(obj, 6, 1, 0)
            примечание = iSpc.ksGetSpcObjectColumnText(obj, 7, 1, 0)

            # в версии 17 почемуто не работает, в 21 материал подгружался к СП
            материал = iSpc.ksGetSpcObjectColumnText(obj, 10, 3, 0)
            fileList = []
            for i in range(DynamicArray.ksGetArrayCount()):
                iDocAttachSpcParam = KompasAPI.module5.ksDocAttachedSpcParam(
                    KompasAPI.api5.GetParamStruct(KompasAPI.const.ko_DocAttachSpcParam))
                DynamicArray.ksGetArrayItem(i, iDocAttachSpcParam)
                fileList.append(iDocAttachSpcParam.fileName)
            if result.get(раздел) == None:
                result[раздел] = []
            result[раздел].append({
                "обозначение": обозначение,
                "наименование": наименование,
                "количество": количество,
                "примечание": примечание,
                "материал": материал,
                "файлы": fileList
            })
            obj = iIter.ksMoveIterator("N")  # чтение cледующей строки
        return result




"""

# вытаскиваем пути на все спецификации
def get_path_spw(ГСП):
    результат = [ГСП]
    РАСШИРЕНИЕ = ".spw"
    for путь in результат:
        объекты = KompasAPI.read_spc(путь)
        if объекты.get("Сборочные единицы") == None: continue
        for СП in объекты.get("Сборочные единицы"):
            for файл in СП.get("файлы"):
                if os.path.splitext(файл)[1] == РАСШИРЕНИЕ and not файл in результат:
                    результат.append(файл)
    return результат


# Вытаскиваем пути на все документы
def get_path_cdw(пути):
    результат_c = []
    результат_д = []
    РАСШИРЕНИЕ = ".cdw"

    for путь in пути:
        объекты = KompasAPI.read_spc(путь)
        if not объекты.get("Сборочные единицы") is None:
            for СБ in объекты.get("Сборочные единицы"):
                for файл in СБ.get("файлы"):
                    if os.path.splitext(файл)[1] == РАСШИРЕНИЕ and not файл in результат_c:
                        результат_c.append(файл)
        if not объекты.get("Детали") is None:
            for Д in объекты.get("Детали"):
                for файл in Д.get("файлы"):
                    if os.path.splitext(файл)[1] == РАСШИРЕНИЕ and not файл in результат_д:
                        результат_д.append(файл)
    return {"сборки": результат_c, "детали": результат_д, "спефикации": пути}

"""
class Database:
    KEYS_DOC = ["обозначение", "наименование", "материал", "формаки"]
    MAX_ID = 1_000_000_000
    con = sqlite3.connect('doc_kompas.sqlite')
    """
    items = {
        # для удобства поиска создают пусты объекты, чтобы возращаемый результа означал не нашел
        "докумены": {None: {KEYS_DOC[0]: None, KEYS_DOC[1]: None, KEYS_DOC[2]: None, KEYS_DOC[3]: None}},
        "материал": {None: ""},
        "покупные": {None: ""}
        # стандартные согласно ГОСТ Р 2.106 также можно записывать в прочие изделия, в СП это прочие изделия
    }
    links = {
        # ТТ: {(id, id): количество}, Т - первая буква ключа словаря items
        "дд": {},
        "дм": {},
        "дп": {}
    }
    """
    @classmethod
    def __generate_id(cls, __table):
        __id = None
        while __id in cls.items.get(__table):
            __id = random.randint(0, cls.MAX_ID)
        return __id

    @classmethod
    def __add(cls, __obj, __type):
        __id = cls.__generate_id(__type)
        cls.items[__type][__id] = __obj
        return __id

    @staticmethod
    def check_obj_doc(obj):
        if not isinstance(obj, dict):
            return False
        keys = Database.KEYS_DOC
        for key in keys:
            if key not in obj.keys():
                return False
        for key in obj.keys():
            if key not in keys:
                return False
        return True

    @classmethod
    def add_doc(cls, obj):
        """
        :param obj: dict() where keys = ["обозначение", "наименование", "материал", "формаки"]
        key "материал" is string, but base int
        :return: id doc
        """
        сообщение = "ошибка формата объекта вызыва функции add_doc(" + str(cls) + ", " + str(obj) + ")"
        if not Database.check_obj_doc(obj):
            print(сообщение)
            return None
        name_material = obj[Database.KEYS_DOC[2]]
        ИСКЛЮЧЕНИЕ = "Изделие-заготовка "
        id_material = 0
        # исключительная ситуация и здесь может быть как ссылка на другоке КД, так и покупное изделие, пока не понятно как с этим работать
        if ИСКЛЮЧЕНИЕ not in name_material:
            id_material = Database.add_materials(name_material)
            obj[Database.KEYS_DOC[2]] = id_material
        else:
            name_material = name_material[len(ИСКЛЮЧЕНИЕ):]
            obj[Database.KEYS_DOC[2]] = name_material[len(ИСКЛЮЧЕНИЕ):]
        id_doc = cls.find_doc_by_designation(obj[cls.KEYS_DOC[0]])
        if id_doc is None:
            id_doc = cls.__add(obj, "докумены")
        if ИСКЛЮЧЕНИЕ not in name_material:
            # create link on material
            cls.__add_links((id_doc, id_material), 0, "дм")
        return id_doc

    @classmethod
    def __find_doc(cls, __str, __type):
        for key in cls.items.get("докумены").keys():
            if __str is cls.items.get("докумены")[key].get(__type):
                return key
        return None

    @classmethod
    def find_doc_by_name(cls, name):
        return cls.__find_doc(name, "наименование")

    @classmethod
    def find_doc_by_designation(cls, designation):
        return cls.__find_doc(designation, "обозначение")

    @classmethod
    def __find(cls, __str, __type):
        for key in cls.items.get(__type).keys():
            if __str is cls.items.get(__type)[key]:
                return key
        return None

    @classmethod
    def __get_item(cls, __id, __type):
        return cls.items.get(__type).get(__id)

    @classmethod
    def __get_link(cls, __ids, __type):
        return cls.links.get(__type).get(__ids)

    @classmethod
    def find_materials(cls, name):
        return cls.__find(name, "материал")

    @classmethod
    def find_products(cls, name):
        return cls.__find(name, "покупные")

    @classmethod
    def add_materials(cls, name):
        obj_id = cls.find_materials(name)
        if obj_id is not None:
            return obj_id
        return cls.__add(name, "материал")

    @classmethod
    def add_products(cls, name):
        obj_id = cls.find_products(name)
        if obj_id is not None:
            return obj_id
        return cls.__add(name, "покупные")

    @classmethod
    def __add_links(cls, __ids, __count, __type):
        if __ids not in cls.links[__type]:
            cls.links[__type][__ids] = 0
        cls.links[__type][__ids] += __count

    @classmethod
    def add_links_doc(cls, main_designation, designation, count):
        id_main = cls.find_doc_by_designation(main_designation)
        id_des = cls.find_doc_by_designation(designation)
        if None in [id_des, id_main]:
            return False
        cls.__add_links((id_main, id_des), count, "дд")
        return True

    @classmethod
    def __find_keys_in_links(cls, __id, __position, __type):
        result = []
        for item in cls.links[__type].keys():
            if item[__position] == __id:
                result.append(item)
        return result

    @classmethod
    def add_links_materials(cls, main_designation, name, count):
        id_main = cls.find_doc_by_designation(main_designation)
        id_des = cls.find_materials(name)
        if None in [id_des, id_main]:
            return False
        cls.__add_links((id_main, id_des), count, "дм")
        return True

    @classmethod
    def add_links_products(cls, main_designation, name, count):
        id_main = cls.find_doc_by_designation(main_designation)
        id_des = cls.find_products(name)
        if None in [id_des, id_main]:
            return False
        cls.__add_links((id_main, id_des), count, "дп")
        return True

    @classmethod
    def print_materials_list(cls):
        for key, item in cls.items["материал"].items():
            if key is None:
                continue
            print(key, "\t", item)
    """
    @classmethod
    def print_materials_detail(cls):
        i = 0
        for key, item in cls.items["материал"]:
            i += 1
            print(i, "\t", item)
            link_keys = cls.__find_keys_in_links(key, 1, "дм")
    """
    @classmethod
    def print_products_list(cls):
        for key, item in cls.items["покупные"].items():
            if key is None:
                continue
            print(key, "\t", item)

    @classmethod
    def print_doc_list(cls):
        i = 0
        for key, item in cls.items["докумены"].items():
            if key is None:
                continue
            i += 1
            string = ""
            for t in range(2):
                string += "\t"+ str(item[Database.KEYS_DOC[t]])
            for key in ["A0", "A1", "A2", "A3", "A4", "A5"]:
                string += "\t" + str(item[Database.KEYS_DOC[3]][key])
            print(i, string)


if __name__ == '__main__':
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    fname = askopenfilename(filetypes=(("Спецификация Компас", "*.spw"),))
    """
    fnames = get_path_spw(fname)
    #paths = get_path_cdw(fnames)
    for path in fnames:
        obj = KompasAPI.read_dok(path)
        Database.add_doc(obj)
        objs = KompasAPI.read_spc(path)

        for key in ["Документация", "Сборочные единицы", "Детали"]:
            lists = objs.get(key)
            if lists is None: continue
            for item in lists:
                doc_path = KompasAPI.get_path_doc(item)
                if doc_path is None: continue
                doc_obj = KompasAPI.read_dok(doc_path)
                Database.add_doc(doc_obj)
                Database.add_links_doc(obj[Database.KEYS_DOC[0]], item[Database.KEYS_DOC[0]], item["количество"])

    print(Database)
    Database.print_doc_list()
    Database.print_materials_list()
    # print(get_path_files(fname))
    # printobjs({1:API_Kompas.read_spc(fname)})
    # objs = get_objs([fname])
    # printobjs (objs)

    # api7.Application.Quit()   # Выходим из программы
    """