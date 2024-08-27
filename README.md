# cluster-comparison

The program is used to compare the results in the log file with the expected data in the CSV file.


## CSV

A .csv file which contains the expected values **MUST** have 3 columns "ArticleID,SectionID,DataID,Value"
e.g.
```
ArticleID,SectionID,DataID,Value
AN-1,DemoContent,BEDARFS-MENGE,1.0
AN-1,DemoContent,KOMPONENTENMENGE,2.0
AN-2,TextHere,RUESTKOSTEN, 50.5
AN-2,TextHere,STL-VARIANT,C
```

## LOG FILE
In the log file, the program requires setting ID keys corresponding to: article, section, data, and value:

#ATA is used for an article
#ATS is used for a section
#ATD is used for a data variable


.log file should be like this:
```
This is the first paragraph of the text.
#ATABEGIN-AN-1
#ATSBEGIN-AlphaBeta
This is the content of a cluster, which includes multiple lines
and may contain special characters like !@#$%^&*.
#ATSEND-AlphaBeta

Other interleaved content.

#ATSBEGIN-SampleText
This text may include numbers such as 12345.
#ATSEND-SampleText

Additional content between clusters.

#ATSBEGIN-AnotherOne
This is the content of cluster.
#ATSEND-AnotherOne

#ATAEND-AN-1

This is the text

#ATABEGIN-AN-2

#ATSBEGIN-DemoContent
Cluster: A complete sentence with punctuation!
This is the content of cluster, which includes multiple lines #ATD-BEDARFS-MENGE=00001,000
This text may include numbers such as 12345 #ATD-KOMPONENTENMENGE=00002,000
#ATSEND-DemoContent

The content continues.

#ATSBEGIN-TestCase
This is the content of cluster, used to test regex.
#ATSEND-TestCase

Intervening text.

#ATSBEGIN-TextHere
This is the content of cluster.
Content of cluster: Various characters @#%^*()! #ATD-RUESTKOSTEN=000050,500
this is the content of cluster #ATD-STL-VARIANT='C'
#ATSEND-TextHere

Continuing text.

#ATSBEGIN-LogEntry
Content of cluster 9: Various characters @#%^*()!
#ATSEND-LogEntry

#ATAEND-AN-2
End of the text.
```


