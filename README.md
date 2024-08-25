# cluster-comparison
 LOG data should be like this:
```
This is the first paragraph of the text.

#ATSBEGIN-randomABC
This is the content of cluster 1.
#ATSEND-randomABC

Some other content between clusters.

#ATSBEGIN-XYZ123
This is the content of cluster 2.
#ATSEND-XYZ123

The text continues here.

#ATSBEGIN-AlphaBeta
This is the content of cluster 3, which includes multiple lines
and may contain special characters like !@#$%^&*.
#ATSEND-AlphaBeta

Other interleaved content.

#ATSBEGIN-SampleText
Cluster 4: This text may include numbers such as 12345.
#ATSEND-SampleText

Additional content between clusters.

#ATSBEGIN-AnotherOne
This is the content of cluster 5.
#ATSEND-AnotherOne

The text continues here.

#ATSBEGIN-DemoContent
Cluster 6: A complete sentence with punctuation!
asdhjkasjdhkj asdkjaslkdjlk aslkdjaslk jlk aslkdjlk #ATD-BEDARFS-MENGE=00001,000
asdw xcyjh 23123 434opxsc oswopdaspodpo pojkmw.ewqlekkl wiqepo #ATD-KOMPONENTENMENGE=00002,000
#ATSEND-DemoContent

The content continues.

#ATSBEGIN-TestCase
This is the content of cluster 7, used to test regex.
#ATSEND-TestCase

Intervening text.

#ATSBEGIN-TextHere
This is the content of cluster 8.
asdw xcyjh 23123 434opxsc oswopdaspodpo pojkmw.ewqlekkl wiqepo #ATD-RUESTKOSTEN=000050,500
asdw xcyjh 23123 434opxsc oswopdaspodpo pojkmw.ewqlekkl wiqepo #ATD-STL-VARIANT='C'
#ATSEND-TextHere

Continuing text.

#ATSBEGIN-LogEntry
Content of cluster 9: Various characters @#%^*()!
#ATSEND-LogEntry

Continuing interleaved content.

#ATSBEGIN-ExampleEnd
Finally, this is the content of cluster 10.
#ATSEND-ExampleEnd

End of the text.
```
