
import sys

class Layer:
    def __init__(self):
        self.m_lvs_layername    = '*'
        self.m_lvs_layernumber  = '*'
        self.m_lvs_datanumber   = '*'
        self.m_layer_type       = 'o'    # 'm' : conducting, 'v' : via, 'm' : marker, 'r' : remove, 'i' : ignore_cap, 'o' : other
        self.m_itf_layername    = '*'
    def GetStr(self):
        return f'{self.m_lvs_layername} {self.m_lvs_layernumber} {self.m_lvs_datanumber} {self.m_layer_type} {self.m_itf_layername}'

class Makegdsmap:
    def __init__(self):
        self.m_gdsmap_filename  = ''
        self.m_pex_lvs_filename = ''
        self.m_mapping_filename = ''
        self.m_input_filename   = ''
        self.m_version          = '20240622.0.0'
        #
        self.m_lvs_layer_dic        = {}    # key : lvs_layername, data : layer
        self.m_itf_layer_dic        = {}    # key : itf_layername, data : [ layer, ... ]
        self.m_input_layers         = []    # [ [ itf_layername, [lvs_layername, ...] ], ... ]
    def PrintUsage(self):
        print(f'# makegdsmap.py({self.m_version}) usage:')
        print(f'% python3 makegdsmap.py gds_map_file pex_lvs_file mapping_file input_file')
        print(f'   gds_map_file : Totem-SC gds.map file(output)')
        print(f'   pex_lvs_file : ICV pex_lvs_map file(input)')
        print(f'   mapping_file : StarRC mapping file(input)')
        print(f'   input_file   : User define file(input)')
        print(f'')
        print(f'   input file format')
        print(f'       itf_layer lvs_layer1 lvs_layer2 ...')
        print(f'       ...')
        print(f'       itf_layer lvs_layer1 lvs_layer2 ...')
        print(f'   input file example')
        print(f'       M1        MET1')
        print(f'       VIA       VIA1')
        print(f'       M2        METAL2')
        print(f'       VIA2      VIA2')
        print(f'       M3        METAL3')
    def ReadArgs(self, args):
        print(f'# read args start') 
        if 5 != len(args):
            self.PrintUsage()
            sys.exit()
        self.m_gdsmap_filename  = args[1]
        self.m_pex_lvs_filename = args[2]
        self.m_mapping_filename = args[3]
        self.m_input_filename   = args[4]
        print(f'# read args end') 
    def PrintInputs(self):
        print(f'# print inputs start')
        print(f'    gds map file : {self.m_gdsmap_filename}')
        print(f'    pex lvs file : {self.m_pex_lvs_filename}')
        print(f'    mapping file : {self.m_mapping_filename}')
        print(f'    input file   : {self.m_input_filename}')
        print(f'# print inputs end')
    # lvs_layer #layer #data
    def ReadPexLVSFile(self):
        print(f'# read pex lvs file({self.m_pex_lvs_filename}) start')
        f = open(self.m_pex_lvs_filename, 'rt')
        lines   = f.readlines()
        for line in lines:
            line    = line.strip()
            tokens  = line.split()
            if 0 == len(tokens):
                continue
            if 3 != len(tokens):
                continue
            lvs_layername   = tokens[0]
            lvs_layernumber = tokens[1]
            lvs_datanumber  = tokens[2]
            if not lvs_layername in self.m_lvs_layer_dic:
                lvs_layer   = Layer()
                lvs_layer.m_lvs_layername   = lvs_layername
                lvs_layer.m_lvs_layernumber = lvs_layernumber
                lvs_layer.m_lvs_datanumber  = lvs_datanumber
                self.m_lvs_layer_dic[lvs_layername] = lvs_layer
        f.close()
        print(f'# read pex lvs file({self.m_pex_lvs_filename}) end')
    def ReadMappingFile(self):
        print(f'# read mapping file({self.m_mapping_filename}) start')
        f = open(self.m_mapping_filename, 'rt')
        layer_type  = 'o'
        lines   = f.readlines()
        for line in lines:
            line    = line.strip()
            tokens  = line.split()
            if 0 == len(tokens):
                continue
            #
            if 1 == len(tokens):
                layer_type  = self.GetLayerType(tokens[0])
            else:
                lvs_layername   = tokens[0]
                itf_layername   = tokens[1]
                #print(f'{lvs_layername} {itf_layername}')
                if lvs_layername in self.m_lvs_layer_dic:
                    lvs_layer                   = self.m_lvs_layer_dic[lvs_layername]
                    lvs_layer.m_itf_layername   = itf_layername
                    lvs_layer.m_layer_type      = layer_type
                    # itf layer 도 lvs_layer_dic에 추가
                    if not itf_layername in self.m_lvs_layer_dic:
                        itf_layer               = Layer()
                        itf_layer.m_lvs_layername   = itf_layername
                        itf_layer.m_itf_layername   = itf_layername
                        itf_layer.m_layer_type      = layer_type
                        self.m_lvs_layer_dic[itf_layername] = itf_layer
                    #
                    if not itf_layername in self.m_itf_layer_dic:
                        lvs_layernames          = []
                        lvs_layernames.append(lvs_layername)
                        self.m_itf_layer_dic[itf_layername] = lvs_layernames
                    else:
                        lvs_layernames          = self.m_itf_layer_dic[itf_layername]
                        lvs_layernames.append(lvs_layername)
        f.close()
        print(f'# read mapping file({self.m_mapping_filename}) end')
    # itf_layername lvs_layername ...
    def ReadInputFile(self):
        print(f'# read input file({self.m_input_filename}) start')
        f = open(self.m_input_filename, 'rt')
        lines   = f.readlines()
        for line in lines:
            line    = line.strip()
            tokens  = line.split()
            if 0 == len(tokens):
                continue
            #
            input_layer     = []
            itf_layername   = tokens[0]
            lvs_layernames  = tokens[1:]
            input_layer.append(itf_layername)
            input_layer.append(lvs_layernames)
            self.m_input_layers.append(input_layer)
        f.close()
        print(f'# read input file({self.m_input_filename}) end')
    def MakeGdsmapFile(self):
        print(f'# make gds map file({self.m_gdsmap_filename}) start')
        try:
            f = open(self.m_gdsmap_filename, 'wt')
        except OSError:
            print(f'# error : could not open file: {self.m_gdsmap_filename}')
            sys.exit()
        #print(f'# debug : input layers size : {len(self.m_input_layers)}')
        for input_layer in self.m_input_layers:
            gdsmap_itf_layername    = input_layer[0]
            lvs_layernames          = input_layer[1]
            #print(f'# debug : {gdsmap_itf_layername} {lvs_layernames}')
            #
            if gdsmap_itf_layername in self.m_lvs_layer_dic:
                itf_layer = self.m_lvs_layer_dic[gdsmap_itf_layername]
                gdsmap_lvs_layer_numbers   = []
                for lvs_layername in lvs_layernames:
                    if lvs_layername in self.m_lvs_layer_dic:
                        lvs_layer   = self.m_lvs_layer_dic[lvs_layername]
                        gdsmap_lvs_layer_numbers.append(lvs_layer.m_lvs_layernumber)
                gdsmap_lvs_layer_numbers_str    = ':'.join(gdsmap_lvs_layer_numbers)
                f.write(f'{gdsmap_itf_layername} {self.GetTTSCLayerType(itf_layer.m_layer_type)} {gdsmap_lvs_layer_numbers_str} -\n')
        f.close()
        print(f'# make gds map file({self.m_gdsmap_filename}) end')
    def PrintLvsLayerDic(self):
        print(f'# print lvs layer dic start.')
        print(f'    lvs_layer_name #layer #data layer_type itf_layer_name')
        for lvs_layername in self.m_lvs_layer_dic:
            lvs_layer   = self.m_lvs_layer_dic[lvs_layername]
            print(f'    {lvs_layer.GetStr()}')
        print(f'# print lvs layer dic end.')
    def PrintITFLayerDic(self):
        print(f'# print itf layer dic start.')
        for itf_layername in self.m_itf_layer_dic:
            lvs_layernames   = self.m_itf_layer_dic[itf_layername]
            lvs_layernames_str  = ' '.join(lvs_layernames)
            print(f'    {itf_layername} {lvs_layernames_str}')
        print(f'# print itf layer dic end.')
    def PrintInputLayers(self):
        print(f'# print input layers start.')
        for input_layer in self.m_input_layers:
            itf_layername   = input_layer[0]
            lvs_layernames  = input_layer[1]
            lvs_layernames_str = ' '.join(lvs_layernames)
            print(f'    {itf_layername} {lvs_layernames_str}')
        print(f'# print input layers end.')
    def GetLayerType(self, token):
        if 'conducting_layers' == token.lower():
            return 'c'
        elif 'via_layers' == token.lower():
            return 'v'
        elif 'marker_layers' == token.lower():
            return 'm'
        elif 'ignore_cap_layers' == token.lower():
            return 'i'
        else:
            return 'o'
    def GetTTSCLayerType(self, layer_type):
        if 'c' == layer_type:
            return 'm'
        else:
            return layer_type
    def Run(self, args):
        print(f'# makegdsmap.py start')
        self.ReadArgs(args)
        self.PrintInputs()
        self.ReadPexLVSFile()
        self.PrintLvsLayerDic()
        self.ReadMappingFile()
        self.PrintLvsLayerDic()
        self.PrintITFLayerDic()
        self.ReadInputFile()
        self.PrintInputLayers()
        self.MakeGdsmapFile()
        print(f'# makegdsmap.py end')

def main(args):
    my_makegdsmap   = Makegdsmap()
    #my_makegdsmap.Run(args)
    # for test
    test_args       = [ 'makegdsmap.py', './tests/test.gds.map', './tests/pex_lvs_map', './tests/mapping_file', './tests/input' ]
    my_makegdsmap.Run(test_args)

if __name__ == '__main__':
    main(sys.argv)