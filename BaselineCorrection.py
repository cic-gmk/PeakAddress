# coding=utf-8
# !/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PeakAddress import peak_recognize_all 
def baseline_correct(X,peak_location_all,path,threshold,percent,X_group):
    ppm_num = 0
    peak_list=[]
    peak_list.append(0)
    #count = 0
    for i in range(peak_location_all.shape[0]):
        #print(peak_location_all.shape[0])
        #进入新一张图的时候的第一段
        if i<(peak_location_all.shape[0]-1) and peak_location_all.iloc[i,0] > peak_location_all.iloc[i+1,1]:
            plt.plot(np.array(X.iloc[ppm_num]),label='raw')
            # if ppm_num ==1:
            #plt.savefig('F:/Chiglitazar/training/NMRData/peaks/%s/peak_%s_%s_%s_raw.png' % (X_group,ppm_num, path, threshold))
            #plt.show()
            #plt.clf()
            peak_list.append(9499)
            print(peak_list)

            startPoint = 0
            startPoint_value = X.iloc[ppm_num, 0]
            for j in range(1,len(peak_list)):
                #遍历和startPoint的组合
                endPoint = peak_list[j]
                endPoint_value = X.iloc[ppm_num, peak_list[j]]
                k = (endPoint_value - startPoint_value) / (endPoint - startPoint)
                b = (endPoint * startPoint_value - startPoint * endPoint_value) / (endPoint - startPoint)
                line = lambda x: k * x + b
                #做出这条线
                temp = []
                #算出谱图的对应直线上的值
                for n in range(startPoint,endPoint):
                    temp.append(line(n))
                count_compare = 0
                #比较曲线和直线的值
                for l in range(0,len(temp)):
                    if temp[l] <= X.iloc[ppm_num, l+startPoint]:
                        count_compare = count_compare + 1
                #满足条件则曲线减掉直线的值，并且终点变为新的起点
                if count_compare / (len(temp)) > percent and endPoint_value>0:
                    for m in range(len(temp)):
                        X.iloc[ppm_num, m+startPoint] = X.iloc[ppm_num, m+startPoint] - temp[m]
                    startPoint = peak_list[j]
                    startPoint_value = endPoint_value
            plt.plot(np.array(X.iloc[ppm_num][:9499]),label='corrected')
            # if ppm_num ==1:
            #plt.savefig('F:/Chiglitazar/training/NMRData/peaks/%s/peak_%s_%s_%s_corrected.png' % (X_group,ppm_num, path, threshold))
            plt.legend()
            plt.show()
            plt.clf()
            peak_list=[]
            peak_list.append(0)
            ppm_num = ppm_num + 1
        else:
            peak_list.append(peak_location_all.iloc[i,0])
            peak_list.append(peak_location_all.iloc[i,1])
    X.to_csv('F:/Chiglitazar/training/NMRData/peaks/NMR_newTrainingData_large_ppm_%s_baseline_corrected_raw.csv' % (X_group))
if __name__ == '__main__':

    X = pd.read_csv("F:/Chiglitazar/training/NMRData/NMR_LargeMolecule_ppm_Training_Placebo.csv",index_col="ppm").T
    peak_recognize_all(X,8,100)
    peak_location_all = pd.read_csv('F:/Chiglitazar/training/NMRData/peaks/peakLocation_large_ppm_Placebo_origin_raw.csv')
    baseline_correct(X,peak_location_all,8,100,0.55,'Placebo')