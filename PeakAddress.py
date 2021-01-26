# coding=utf-8
# !/usr/bin/env python3
import os, re, argparse, sys
import numpy as np
import pandas as pd
USAGE = 'Usage: python PeakAddress.py spectrum_data.csv -o newData.csv' 
def increase_or_decrease(intensity_value,num,path):
    #判断趋势
    if intensity_value[num+path] > intensity_value[num]:
        flag = 1
    else:
        flag = 0
    return flag

def increase_or_decrease_next(intensity_value,num,path):
   #迭代判断趋势
    times_count = 0
    if increase_or_decrease(intensity_value,num,path) == increase_or_decrease(intensity_value,num+path,path):
        times_count = increase_or_decrease_next(intensity_value,num+path,path) + 1
    else:
        return times_count
    return times_count

def peak_recognize(intensity_value,path=1,threshold=400):
    #输入一张谱图数据，输出该图的所有峰起点终点
    peak_location = []
    num_now = 0
    for i in range(intensity_value.shape[0]):
        try:
            if i < num_now:
                continue
            else:
                if increase_or_decrease(intensity_value,i,path) == increase_or_decrease(intensity_value,i+path,path):
                    startPoint = i
                    turnningPoint= i+(increase_or_decrease_next(intensity_value,i,path)+1)*path
                    endPoint = turnningPoint + increase_or_decrease_next(intensity_value,turnningPoint,path)*path
                    if increase_or_decrease(intensity_value,i,path) == 1:
                        if (intensity_value[startPoint:endPoint].max()-intensity_value[startPoint])/(intensity_value[startPoint:endPoint].argmax()+1) > threshold:
                            num_now = endPoint
                            peak_location.append([startPoint, endPoint])
                        else:
                            num_now = endPoint
                            continue
                    elif increase_or_decrease(intensity_value,i,path) == 0:
                        if abs((intensity_value[startPoint:endPoint].min() - intensity_value[startPoint]) )/ \
                                (intensity_value[startPoint:endPoint].argmin() + 1) > threshold:
                            num_now = endPoint
                            peak_location.append([startPoint, endPoint])
                        else:
                            num_now = endPoint
                else:
                    continue
        except:
            break
    print(len(peak_location),end=' ',flush=True)

    return pd.DataFrame(peak_location)

def peak_recognize_all(X,path=3,threshold=400,intermediate=False,output_dir = None):
    #输入所有样本数据，输出所有样本的峰位置（起点和终点），保存在文件中
    peak_location_all = pd.DataFrame()
    print('The peaks amount of every pic',end=':')
    for i in range(X.shape[0]):
        intensity_value = np.array(X.iloc[i])
        peak_location_all = pd.concat([peak_location_all,peak_recognize(intensity_value,path,threshold)])

    print('\nThe peaks amount of all pics:',peak_location_all.shape[0])
    if intermediate:
        peak_location_all.to_csv(output_dir,index=False)
    peak_location_all = peak_location_all.reset_index()
    peak_location_all = peak_location_all.drop(['index'],axis=1)

    return peak_location_all
def peak_demix(peak_location_all,overlap_rate=0.7,intermediate=False,output_dir = None):
    #合并相互重叠超过 overlap_rate 的峰 否则保留 
    print('Left peaks amount:',end='')
    
    for i in range(peak_location_all.shape[0]):

        try:
            for j in range(i+1,peak_location_all.shape[0]):
    #             print(j)
                peak_a_start=peak_location_all.iloc[i,0];peak_a_end=peak_location_all.iloc[i,1]
                peak_a_range = peak_a_end - peak_a_start
                peak_b_start=peak_location_all.iloc[j,0];peak_b_end=peak_location_all.iloc[j,1]
                peak_b_range = peak_b_end - peak_b_start
                demix_start = max(peak_a_start,peak_b_start)
                demix_end = min(peak_a_end,peak_b_end)
                overlap = demix_end - demix_start
                if overlap>0 and overlap/peak_a_range>overlap_rate and overlap/peak_b_range>overlap_rate:

                    peak_location_all.iloc[i,0] = demix_start
                    peak_location_all.iloc[i,1] = demix_end
                    peak_location_all = peak_location_all.drop(j)

                    peak_location_all = peak_location_all.reset_index()
                    peak_location_all = peak_location_all.drop(['index'], axis=1)
        except:
            print(j,end=' ',flush=True)
            continue


    print('\nThe last left peaks amount:',peak_location_all.shape[0])
    if intermediate:
        peak_location_all.to_csv(output_dir,index=False)
    return peak_location_all
def peak_area(intensity_value,startPoint,endPoint):
    #峰面积计算
    peakArea = 0
    for i in range(startPoint,endPoint):
        if intensity_value[i] > 0:
            peakArea = peakArea + (abs(intensity_value[i]) + abs(intensity_value[i + 1])) * 0.5
        else:
            peakArea = peakArea - (abs(intensity_value[i])+abs(intensity_value[i+1]))*0.5

    return peakArea

def peak_area_all(X,peak_location_all):
    #计算所有峰面积生成新的训练文件
    peak_newData = pd.DataFrame(np.zeros(X.shape[0]*peak_location_all.shape[0]).reshape(X.shape[0],peak_location_all.shape[0]))
    for i in range(X.shape[0]):
        intensity_value = np.array(X.iloc[i])
        for j in range(peak_location_all.shape[0]):
            peak_newData.iloc[i,j] = peak_area(intensity_value,peak_location_all.iloc[j,0],peak_location_all.iloc[j,1]).round(0)
#     print(peak_newData)
#     peak_newData.to_csv(work_dir + r'\peaks\NMR_newTrainingData.csv' ,index=False)
    return peak_newData
def parseArgs(argv):
    parser = argparse.ArgumentParser(prog="PeakAddress.py", description=USAGE, \
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("spectrum_data", type=str, \
                        help="Input original spectrum data ")
    parser.add_argument("-o", "--output", type=str, default=None, \
                        help="Output dir")
    thresg = parser.add_argument_group("Peak Recognition Threshold Arguments")
    thresg.add_argument("-p", "--path", type=int, default=1, \
                        help="The path of peak recognition (1)")
    thresg.add_argument("-t", "--threshold", type=int, default=400, \
                        help="The rate of increase or decrease of the peak (400)")
    thresg.add_argument("-O", "--overlap_rate", type=float, default=0.7, \
                        help="Reciprocal overlaps between peaks to be demixed (0.7)")
    optimg = parser.add_argument_group("Optimization Arguments")
    optimg.add_argument("-b", "--baselinecorrect", type=bool, default=False, \
                        help="Whether correct the baseline of the raw data (False)")
    optimg.add_argument("-i", "--intermediate", type=bool, default=False, \
                        help="Whether output the intermediate peak location files (False)")


    args = parser.parse_args(argv)

    #     setupLogging(args.debug)

    return args
def runmain(argv):
    # spectrum_data, output,path=1, threshold = 400, overlap_rate = 0.7, intermediate
    args = parseArgs(argv)

    spectrum_data_dir = args.spectrum_data
    path = args.path
    threshold = args.threshold
    overlap_rate = args.overlap_rate
    intermediate = args.intermediate
    if intermediate:
        output_dir_main = args.output[:args.output.rindex('.')]
        original_peak_location_output_dir = output_dir_main+'_original_peak_location.csv'
        demixed_peak_location_output_dir = output_dir_main+'_demixed_peak_location.csv'
    spectrum_data = pd.read_csv(spectrum_data_dir,index_col="ppm").T
    demixed_peak_location = peak_demix(peak_recognize_all(spectrum_data,path,threshold,intermediate,original_peak_location_output_dir),\
                                       overlap_rate,intermediate,demixed_peak_location_output_dir)
    newData = peak_area_all(spectrum_data,demixed_peak_location)
    newData['peaks'] = spectrum_data.index
    newData = newData.set_index('peaks')
    print(newData)
    newData.to_csv(args.output)
    return
if __name__ == '__main__':
    runmain(sys.argv[1:])
#python PeakAddress.py C:\Users\gmk\Desktop\chigli\training\NMRData\NMR_SmallMolecule_ppm_Training_Placebo.csv -o C:\Users\gmkly\Desktop\chigli\training\NMRData\123.csv -i True