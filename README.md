### SDG database

The separator for the csv file is the tabulation.

```python
import pandas as pd
df = pd.read_csv("../WoS_SDG.csv", sep="\t", encoding='utf-8', index_col=False, na_values='N/A')
# or 
df = pd.read_pickle("../WoS_SDG.pkl")
```


#### Column names

Web of Science Tags are available : [Here](https://images.webofknowledge.com/images/help/WOS/hs_wos_fieldtags.html)

| Column name              | Name                                                |                                                            Description |
|:-------------------------|:----------------------------------------------------|-----------------------------------------------------------------------:|
| PT                       | Publication Type                                    |                                        Journal, Book, Series or Patent |
| AU                       | Authors                                             |                               List of authors separated by a semicolon |
| TI                       | Title                                               |                                           The title of the publication |
| SO                       | Publication Name                                    |                                                    Name of the Journal |
| DE                       | Author Keywords                                     |                               A list of keywords chosen by the authors |
| AB                       | Abstract                                            |                                        The abstract of the publication |
| C1                       | Author address                                      |               The full address of each author separated by a semicolon |
| EM                       | E-mail address                                      |               Address e-emails of each author separated by a semicolon |
| TC                       | Web of Science Core Collection Times Cited Count    |                     The number of times the publication has been cited |
| PY                       | Publication year                                    |                                                Year of the publication |
| WC                       | Web of Science Categories                           |                               A list of categories from Web of Science |
| UT                       | Accession Number                                    |                                Web of Science's ID for the publication |
| CN                       | Countries                                           |         A list of all countries having collaborated on the publication |
| SDG 1-17                 | SDG 1-17                                            |               A boolean to show if the publication deals with said SDG |
| AI                       | Artificial intelligence                             |                     A boolean to show if the publication deals with AI |
| big_data                 | Big Data                                            |               A boolean to show if the publication deals with big data |
| IOT                      | Internet of Things                                  |                    A boolean to show if the publication deals with IOT |
| computing_infrastructure | Computing infrastructure                            |                     A boolean to show if the publication deals with CI |
| blockchain               | Blockchain                                          |             A boolean to show if the publication deals with blockchain |
| robotics                 | Robotics                                            |               A boolean to show if the publication deals with robotics |
| additive_manufacturing   | Additive manufacturing                              | A boolean to show if the publication deals with additive manufacturing |
| Society                  | Society                                             |   A boolean, True if publication is part of SDG 1,2,3,4,5,6,7,11 or 16 |
| Economy                  | Economy                                             |         A boolean, True if publication is part of SDG 8,9, 10,12 or 17 |
| Environment              | Environment                                         |              A boolean, True if publication is part of SDG 13,14 or 15 |  

  
<br/><br/>

#### Keywords for SDG classification  

Keywords are available : [Here](https://aurora-network-global.github.io/sdg-queries/)

#### Publication Year
We have chosen to keep publications released between 2010 and 2021.  

#### Language
ALl the publications of this database are written in English.  

#### Acquisition
Raw data was downloaded from Web of Science in February 2022