#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 19:00:47 2020

@author: mrinalini
"""

t=int(input())

for _ in range(t):
    n=int(input())
    count=0
    arr=list(map(int,input().split()))
    for i in range(n-1):
        for j in range(i+1,n):
            if(arr[i]>arr[j] or arr[i]<arr[j]):
                count+=1
    print(count)
    
    
    #a=b 
    #p>j p<j
    
    
    
    