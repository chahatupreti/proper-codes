# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 14:55:00 2016

@author: Krishna
"""
print 56
import os
ccount = 0
uncount = 0
count = 0
wcount = 0
a=''
for path, dirs, files in os.walk(r'L:\My Online Documents\MTech\GEO_website\series\new series files'):
    #print 44
    for file in files:
        #print 5
        read_f = open(os.path.join(path,file),'r')
        #print file
        a=str(file)
        if a=='README.txt':
            break
        b=a[3:8]
        b=int(b)
        if b in range(14881,17721):
            
            output = open(os.path.join('L:\My Online Documents\MTech\series_imp_info', file + 'imp_info.txt'),'w');
            for line in read_f:
                line = line.rstrip()
                if line.startswith('!Series_title'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Series_summary'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Sample_organism_ch1'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Series_overall_design'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Sample_title'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Sample_source_name_ch1'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Sample_characteristics_ch1'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Sample_treatment_protocol_ch1'):
                    output.write(line);
                    output.write('\n');
                if line.startswith('!Sample_description'):
                    output.write(line);
                    output.write('\n');
                if line == '!series_matrix_table_begin':
                    break
        
        output.close()
        read_f.close()
