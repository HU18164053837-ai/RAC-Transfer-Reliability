## Databases for synergistic multi-performance optimization of recycled aggregate concrete using explainable machine learning and NSGA-III





### 1\. Dataset Overview



This dataset comprises two databases of recycled aggregate concrete compiled from publicly available Chinese academic literature. The databases are intended for the machine-learning prediction of the 28-day compressive strength and slump of recycled aggregate concrete.



The original compressive-strength database contains 1,736 records. Following outlier detection using the Isolation Forest algorithm, 1,649 records were used to train and test the machine-learning models, while 87 records were identified as outliers.



The original slump database contains 1,032 records. Following outlier detection using the Isolation Forest algorithm, 980 records were used to train and test the machine-learning models, while 52 records were identified as outliers.



To ensure data integrity and traceability, both databases retain all records collected before outlier detection. The source of each record can be identified through the source\_reference column in the corresponding data file and the “Source References” section at the end of this README.



All data were manually extracted and entered from the source publications. Although the data were checked and verified during compilation, errors may remain due to manual identification, transcription, or interpretation of tables and figures in the original publications. Users are therefore advised to verify any specific record against the original publication indicated by source\_reference.





### 2\. File Description



This dataset contains the following files:



(1) compressive\_strength\_database.xlsx



A recycled aggregate concrete compressive-strength database containing 1,736 records and 15 variables. The target variable is the 28-day compressive strength after conversion to an equivalent value for a standard specimen size.



(2) slump\_database.xlsx



A recycled aggregate concrete slump database containing 1,032 records and 15 variables. The target variable is the measured slump.



(3) README.md



This file provides an overview of the dataset, data-collection methods, variable definitions, the outlier-detection method, instructions for use, dataset limitations, and source references.



Both databases are provided as Microsoft Excel workbooks (XLSX). Each file contains one worksheet. The first row contains the variable names, and each subsequent row represents an independent data record.





### 3\. Data Sources and Selection Criteria



The data were collected from publicly available Chinese academic literature. The following criteria were applied during data collection and screening:



(1) Only records for which complete mixture-proportion parameters, recycled coarse aggregate properties, and target performance values were available were included.



(2) All target values in the compressive-strength database correspond to the 28-day compressive strength.



(3) Compressive-strength results obtained using nonstandard 100 mm cubic specimens were converted to equivalent values for standard 150 mm cubic specimens.



(4) The quantities of all concrete constituents were standardized to kg/m³.



(5) Proportional variables, including recycled coarse aggregate properties and replacement ratio, are expressed as percentages.



(6) Different concrete mixture proportions reported in the same publication were treated as independent records.



(7) Data were excluded when the meaning of a variable, its unit, or the relevant test conditions could not be determined.



(8) The source\_reference value for each record corresponds to a numbered publication in the “Source References” section at the end of this README.





### 4\. Data Harmonization



To reduce inconsistencies in data reporting among the source publications, the following definitions and harmonization procedures were adopted:



ρ-RCA denotes the apparent density of recycled coarse aggregate.



CV-RCA denotes the crushing value of recycled coarse aggregate.



W-RCA denotes the water absorption of recycled coarse aggregate.



CA denotes the total amount of natural and recycled coarse aggregates, i.e., the total coarse aggregate content, in kg/m³. The relative proportions of the two types of coarse aggregate are determined by RAR.



RAR denotes the recycled coarse aggregate replacement ratio.



SP denotes the mass of superplasticizer, in kg/m³.



CS denotes the 28-day compressive strength after conversion to an equivalent value for a standard specimen size.



SL denotes the measured slump.



A value of 0 mm in the slump database represents a genuine zero-slump test result and does not indicate a missing value.



FA=0, GGBS=0, or SP=0 indicates that the corresponding material was not included in the mixture and does not indicate a missing value.



RAR=0 indicates that no recycled coarse aggregate was used in the mixture and does not indicate a missing value.



Neither database contains missing values in its numerical variables. Records with incomplete information or ambiguous variable definitions were excluded during data collection.





### 5\. Outlier Detection



The Isolation Forest algorithm was applied separately to the compressive-strength and slump databases. All numerical variables except record\_id, source\_reference, and outlier\_flag were used for outlier detection. The data were not standardized, and all parameters not listed below were set to the scikit-learn defaults.



The principal Isolation Forest parameters were:



n\_estimators: 100



contamination: 0.05



random\_state: 42



The outlier\_flag column in each data file indicates the result of outlier detection:



outlier\_flag=0: The record was not identified as an outlier and was used for machine-learning modeling.



outlier\_flag=1: The record was identified as an outlier and was not used for machine-learning modeling in the associated study.



The compressive-strength database contains 1,736 original records, of which 1,649 have outlier\_flag=0 and 87 have outlier\_flag=1.



The slump database contains 1,032 original records, of which 980 have outlier\_flag=0 and 52 have outlier\_flag=1.



The Isolation Forest outlier-detection code is not included in this dataset. However, the classification result for every record is provided through outlier\_flag. Filtering the data to retain records with outlier\_flag=0 reproduces the modeling datasets used in the associated study. The outlier-detection code is available from the authors upon request.





### 6\. Variable Dictionary



The following variables apply to both databases unless otherwise stated. Variables specific to either the compressive-strength or slump database are identified separately.



record\_id:



A unique identifier for each record. The compressive-strength database uses identifiers such as CS\_0001 and CS\_0002, while the slump database uses identifiers such as SL\_0001 and SL\_0002.



source\_reference:



The numbered reference identifying the source publication. Values such as \[1] and \[2] correspond to the numbered publications in the “Source References” section at the end of this README.



ρ-RCA (kg/m3):



Apparent density of recycled coarse aggregate, in kg/m³.



CV-RCA (%):



Crushing value of recycled coarse aggregate, in %.



W-RCA (%):



Water absorption of recycled coarse aggregate, in %.



Cement (kg/m3):



Cement content, in kg/m³.



FA (kg/m3):



Fly ash content, in kg/m³.



GGBS (kg/m3):



Ground granulated blast-furnace slag content, in kg/m³.



Water (kg/m3):



Mixing-water content, in kg/m³.



Sand (kg/m3):



Fine aggregate content, in kg/m³.



CA (kg/m3):



Total content of natural and recycled coarse aggregates, in kg/m³.



RAR (%):



Recycled coarse aggregate replacement ratio, in %.



SP (kg/m3):



Superplasticizer content, in kg/m³.



CS (MPa):



The 28-day compressive strength after conversion to an equivalent value for a standard specimen size, in MPa. This variable appears only in the compressive-strength database.



SL (mm):



Measured slump, in mm. This variable appears only in the slump database.



outlier\_flag:



The result of Isolation Forest outlier detection. A value of 0 indicates that the record was used for modeling, while a value of 1 indicates that it was excluded from modeling.





### 7\. Instructions for Use



Both XLSX files retain all records collected before outlier detection.



To obtain the data used to train and test the models in the associated study, filter the records to retain outlier\_flag=0. The resulting datasets should contain:



Compressive-strength data: 1,649 records.



Slump data: 980 records.



The source of each record can be traced through source\_reference. For example, \[1] in a data file corresponds to Reference \[1] in the “Source References” section of this README.



When using this dataset for model training or performance prediction, users are advised to keep the input parameters within the ranges represented in the databases. Predictions outside these ranges are extrapolations and require further validation.





### 8\. Data Quality Control



The following quality-control checks were performed before the dataset was released:



(1) The uniqueness and continuity of record\_id values were checked.



(2) Variable names and units were checked for consistency.



(3) The data were checked for missing, negative, and infinite values.



(4) The numbers of records with each outlier flag were checked against the modeling sample sizes reported in the associated study.



(5) The correspondence between source\_reference values and source publications was checked.



(6) The completeness of individual records was checked.



(7) Records with a slump of 0 mm were confirmed to be genuine experimental results.



Despite careful data extraction and quality-control procedures, transcription errors may remain. Users are advised to verify critical records against the original sources cited in the reference list.





### 9\. Dataset Limitations



Users should consider the following limitations:



(1) The data were collected from different studies; therefore, the origins of the raw materials and recycled aggregates, processing methods, and test environments may differ.



(2) The databases include only the principal input variables used in the associated machine-learning models. Other experimental parameters reported in some source publications were not included.



(3) Compressive-strength results obtained using different specimen sizes were converted to equivalent values for a standard specimen size, but the original specimen size was not retained as a model input variable.



(4) Most data were obtained from Chinese academic literature. The applicability of the dataset may therefore be constrained by the materials and experimental conditions represented in the available studies.



(5) The superplasticizer data represent the product mass reported in each publication. Solid content and composition may differ among products.



(6) Data-driven models developed using these databases are primarily applicable within the ranges of the included variables. Predictions outside these ranges should be interpreted with caution.



(7) All data were manually extracted and entered. Some records may differ from the original publications because of limited figure or table clarity, differences in data presentation, or manual transcription.





### 10\. Associated Manuscript



The associated manuscript has not yet been published. Full citation details will be added in a future version of the dataset after publication.





### 11\. Source References



The source\_reference column corresponds to the numbered publications listed below. All source publications are in Chinese. English titles provided by the original publications or journals were used whenever available. Where no official English title was available, an accurate English translation is provided and the reference is marked “(In Chinese).”





\[1] H.Y. Huo, C.C. Fan, A.J. Chen, et al. Influence of recycled aggregate with different strength grades on basic mechanical properties of recycled concrete\[J]. Concrete, 2017(2): 60-62,65. https://doi.org/10.3969/j.issn.1002-3550.2017.02.016. (In Chinese).



\[2] M.H. Zhou, L.J. Li. Experimental study and analysis on strength of recycled aggregate concrete\[J]. Concrete, 2011(5): 99-101. https://doi.org/10.3969/j.issn.1002-3550.2011.05.034. (In Chinese).



\[3] K.C. Xu, W.P. Wang, L.Q. Zhang. Compressive strength of mixed recycled concrete with coarse aggregates from different sources and its prediction model establishment\[J]. Materials Reports, 2025, 39(12): 86-94. https://doi.org/10.11896/cldb.23110068. (In Chinese).



\[4] W.B. Wang. Study on influence of different recycled coarse aggregates on mechanical properties of concrete\[J]. Jiangxi Building Materials, 2024(7): 24-26. (In Chinese).



\[5] Y.D. Zhang, J.S. Zhang, J.L. Jia, et al. Pore structure and mechanical properties analysis of recycled concrete with full replacement of coarse aggregate\[J]. Bulletin of the Chinese Ceramic Society, 2024, 43(8): 3005-3016,3033. (In Chinese).



\[6] S.L. Zhu, X. Wang. Analysis of influence of recycled coarse aggregate replacement rate on mechanical properties of concrete\[J]. Jiangxi Building Materials, 2024(2): 14-16. https://doi.org/10.3969/j.issn.1006-2890.2024.02.009. (In Chinese).



\[7] A.L. Zhang, G.H. Tian, Y.F. Guo. Study on mechanical and pavement performance of recycled concrete under different strength grades\[J]. Concrete, 2023(12): 192-195. https://doi.org/10.3969/j.issn.1002-3550.2023.12.039. (In Chinese).



\[8] H. Meng, Q.Y. Li. Strength prediction of recycled concrete based on BP network\[C]//Proceedings of the 3rd National Symposium on Recycled Concrete. 2012: 208-215. (In Chinese).



\[9] W. Gao. Prediction of compressive strength of recycled concrete based on deep learning\[J]. Concrete, 2018(11): 58-61,70. https://doi.org/10.3969/j.issn.1002-3550.2018.11.015. (In Chinese).



\[10] T.W. He. Study on mechanical properties of GFRP-confined recycled concrete-filled steel tubular stub columns\[D]. Chang'an University, 2023. (In Chinese).



\[11] Z.Q. Zhong. Study on axial compression bearing capacity of medium-long columns of recycled coarse aggregate self-compacting concrete-filled steel tubes\[D]. Lanzhou Jiaotong University, 2023. (In Chinese).



\[12] C.M. Huang. Experimental study on mechanical properties of fly ash recycled concrete\[J]. Brick-Tile, 2023(3): 30-33. https://doi.org/10.3969/j.issn.1001-6945.2023.03.003. (In Chinese).



\[13] D.Q. Zhu. Experimental study and engineering application of influence of recycled coarse aggregate on concrete performance\[J]. Jushe, 2023(6): 178-180. (In Chinese).



\[14] L. Liu. Experimental study on compressive strength and elastic modulus of recycled concrete\[J]. Value Engineering, 2020, 39(36): 138-139. (In Chinese).



\[15] R. Yang, M.Y. Hang. Effect of fly ash (Grade II) content on performance of recycled aggregate concrete\[J]. Low Temperature Architecture Technology, 2022, 44(2): 82-84,89. https://doi.org/10.13905/j.cnki.dwjz.2022.02.016. (In Chinese).



\[16] Q. Zhou, X.Y. Chen, S.K. Cheng, et al. Effect of recycled coarse aggregate on performance of concrete with different strength grades\[J]. Journal of Wuhan Institute of Technology, 2022, 44(5): 534-539. https://doi.org/10.19843/j.cnki.CN42-1779/TQ.202111014. (In Chinese).



\[17] W. Gan. Study on effect of fly ash content on performance of construction waste recycled concrete\[J]. Western China Communications Science \& Technology, 2022(9): 43-45. https://doi.org/10.13282/j.cnki.wccst.2022.09.016. (In Chinese).



\[18] F. Jiang. Study on influence of sand ratio and water-cement ratio on compressive performance of recycled concrete\[J]. Heilongjiang Hydraulic Science and Technology, 2021, 49(4): 62-65,140. https://doi.org/10.3969/j.issn.1007-7596.2021.04.020. (In Chinese).



\[19] G.L. Wang, S.Y. Qi, J.Y. Li, et al. Experimental study on mechanical properties of recycled coarse aggregate concrete\[J]. Concrete, 2020(3): 168-171,176. https://doi.org/10.3969/j.issn.1002-3550.2020.03.041. (In Chinese).



\[20] X. Gao, N. Wang. Experimental study on compressive strength of recycled concrete\[J]. Cement Engineering, 2020(4): 29-30,34. https://doi.org/10.13697/j.cnki.32-1449/tu.2020.04.008. (In Chinese).



\[21] L. Zhang, Z.P. Yu, L. Shen, et al. Study on size effect of compressive strength of recycled concrete with different replacement rates\[J]. New Building Materials, 2019, 46(3): 18-21,87. https://doi.org/10.3969/j.issn.1001-702X.2019.03.005. (In Chinese).



\[22] W.P. Wu, F.S. Duan, C.H. Qian, et al. Study on compressive performance of recycled concrete with different replacement rates of type II coarse aggregate\[J]. Jushe, 2019(22): 30. (In Chinese).



\[23] H.X. Qiao, L.J. Guan, H. Cao, et al. Mechanical properties of recycled aggregate concrete with different mix proportions\[J]. Journal of Lanzhou University of Technology, 2018, 44(3): 142-145. https://doi.org/10.3969/j.issn.1673-5196.2018.03.027. (In Chinese).



\[24] K.T. Xiao. Study on performance and modification of recycled concrete\[D]. Wuhan University of Technology, 2004. (In Chinese).



\[25] J.B. Li, J.Z. Xiao, Z.P. Sun. Characteristics of recycled coarse aggregate and its influence on recycled concrete performance\[J]. Journal of Building Materials, 2004(4): 390-395. https://doi.org/10.3969/j.issn.1007-9629.2004.04.006. (In Chinese).



\[26] J.Z. Xiao, J.B. Li, Z.P. Sun, et al. Study on compressive strength of recycled concrete\[J]. Journal of Tongji University (Natural Science), 2004, 32(12): 1558-1561. https://doi.org/10.3321/j.issn:0253-374X.2004.12.002. (In Chinese).



\[27] Y.Z. Ye, S.W. Pan, G.H. Li, et al. Experimental study on preparation of high-performance recycled concrete\[J]. Construction Technology, 2005(S2): 82-84,91. (In Chinese).



\[28] S.H. Liu, K.H. Fang, L. Zeng. Experimental study on mechanical properties of recycled concrete\[C]//Proceedings of the 2005 National Symposium on Fly Ash Utilization Technology. 2005: 30-32. (In Chinese).



\[29] G.Y. Cheng. Experimental study on basic properties of concrete with different recycled aggregate replacement rates\[J]. Concrete, 2005(11): 67-70. https://doi.org/10.3969/j.issn.1002-3550.2005.11.019. (In Chinese).



\[30] K. Li. Study on basic properties of recycled aggregate and recycled concrete\[D]. Dalian University of Technology, 2006. (In Chinese).



\[31] Y.H. Jiang. Study on compressive strength and mix proportion design of recycled concrete\[D]. Nanjing University of Aeronautics and Astronautics, 2006. (In Chinese).



\[32] D.Q. Shen. Study on performance of recycled aggregate concrete\[D]. Beijing Jiaotong University, 2006. (In Chinese).



\[33] T. Du. Experimental study on microstructure and performance of high-performance recycled concrete\[D]. Huazhong University of Science and Technology, 2006. (In Chinese).



\[34] Y.C. Zeng, J. Yin. Experimental study on recycled concrete\[J]. Journal of Hunan University of Technology (Social Science Edition), 2006, 11(2): 19-23. https://doi.org/10.3969/j.issn.1674-117X.2006.02.005. (In Chinese).



\[35] J.X. Zhang, J.H. Zhang, C.S. Wu. Study on performance and pore structure of recycled concrete\[J]. Journal of Building Materials, 2006, 9(2): 142-147. https://doi.org/10.3969/j.issn.1007-9629.2006.02.003. (In Chinese).



\[36] X.D. Lu, Y.Z. Ye, Z.R. Yan. Study on compressive strength of high-strength concrete with recycled aggregate\[J]. Subgrade Engineering, 2007(4): 105-107. https://doi.org/10.3969/j.issn.1003-8825.2007.04.052. (In Chinese).



\[37] W. Xu. Influence of recycled coarse aggregate replacement rate on basic properties of concrete\[J]. Concrete, 2006(9): 45-47. https://doi.org/10.3969/j.issn.1002-3550.2006.09.014. (In Chinese).



\[38] J.F. Lin, Y.S. Sheng, H.Y. Xing. Experimental study on compressive strength of recycled concrete\[J]. Bulletin of Science and Technology, 2006, 22(6): 807-812. https://doi.org/10.3969/j.issn.1001-7119.2006.06.017. (In Chinese).



\[39] M.P. Hu. Mechanical properties of recycled coarse aggregate concrete with different replacement rates\[J]. Concrete, 2007(2): 52-54. https://doi.org/10.3969/j.issn.1002-3550.2007.02.016. (In Chinese).



\[40] J. Zhang. Study on recycled concrete and mechanical performance analysis of recycled concrete columns\[D]. Southwest Jiaotong University, 2007. (In Chinese).



\[41] J. Zhao, Z.H. Deng, J. Lin. Experimental study on performance of recycled concrete coarse aggregate\[J]. China Building Materials Science \& Technology, 2007, 16(4): 17-20. https://doi.org/10.3969/j.issn.1003-8965.2007.04.005. (In Chinese).



\[42] Z.W. Wang. Basic properties of recycled aggregates from different sources and their influence on compressive strength of concrete\[J]. New Building Materials, 2007, 34(7): 57-60. https://doi.org/10.3969/j.issn.1001-702X.2007.07.019. (In Chinese).



\[43] J. Tang. Preliminary study on compressive strength of recycled concrete\[J]. Sichuan Building Science, 2007, 33(4): 183-186. https://doi.org/10.3969/j.issn.1008-1933.2007.04.049. (In Chinese).



\[44] L.S. Li, Y.L. Peng, A.M. Gong, et al. Analysis on influence of different replacement rates of recycled coarse aggregate on workability and strength of concrete\[J]. Concrete, 2007(8): 41-43. https://doi.org/10.3969/j.issn.1002-3550.2007.08.013. (In Chinese).



\[45] S.H. You. Experimental study on performance of recycled coarse aggregate concrete\[J]. Municipal Engineering Technology, 2007, 25(5): 423-426,428. https://doi.org/10.3969/j.issn.1009-7767.2007.05.026. (In Chinese).



\[46] Y.D. Xu, J.S. Shen. Experimental study on high-performance improvement of recycled concrete\[J]. Concrete, 2007(9): 37-38,41. https://doi.org/10.3969/j.issn.1002-3550.2007.09.010. (In Chinese).



\[47] B. Yu. Study on basic properties of recycled coarse aggregate concrete\[D]. Nanchang University, 2007. (In Chinese).



\[48] J.Z. Xiao. Experimental study on complete stress-strain curve of recycled concrete under uniaxial compression\[J]. Journal of Tongji University (Natural Science), 2007, 35(11): 1445-1449. https://doi.org/10.3321/j.issn:0253-374X.2007.11.001. (In Chinese).



\[49] J.G. Shi, Y.Z. Xu. Experimental study and calculation analysis on influence of aggregate grading on strength and workability of recycled concrete\[J]. Concrete, 2008(1): 82-86. https://doi.org/10.3969/j.issn.1002-3550.2008.01.025. (In Chinese).



\[50] L. Sun, D.X. Qian. Experimental analysis on influence of recycled coarse aggregate replacement rate on workability of recycled concrete\[J]. Henan Building Materials, 2008(1): 43-44. https://doi.org/10.3969/j.issn.1008-9772.2008.01.028. (In Chinese).



\[51] H. Zhou, A.M. Gong, C.M. Jiang, et al. Influence of recycled coarse aggregate replacement rate on mechanical properties of concrete\[J]. West-China Exploration Engineering, 2008, 20(5): 158-160,164. https://doi.org/10.3969/j.issn.1004-5716.2008.05.064. (In Chinese).



\[52] X. Xiao, W. Huang, M.Y. Shen, et al. Experimental study on axial compression of rubber aggregate concrete filled steel tubular stub columns\[J]. Journal of Experimental Mechanics, 2021, 36(6): 771-782. https://doi.org/10.7520/1001-4888-20-244. (In Chinese).



\[53] F. Yu, S.C. Deng. Study on compressive strength of recycled concrete\[J]. Industrial \& Science Tribune, 2009, 8(1): 126-127. https://doi.org/10.3969/j.issn.1673-5641.2009.01.056. (In Chinese).



\[54] A.J. Chen, J. Wang, Q. Zhang. Orthogonal analysis on basic properties of recycled coarse aggregate concrete\[J]. Concrete, 2009(1): 79-83. https://doi.org/10.3969/j.issn.1002-3550.2009.01.023. (In Chinese).



\[55] S.H. Liu. Experimental study on high-performance recycled aggregate concrete\[J]. Journal of Shenyang Jianzhu University (Natural Science), 2009, 25(2): 262-266. (In Chinese).



\[56] D.H. Wang, J. Yin, S.X. Peng. Study on correlation between compressive strength and splitting tensile strength of recycled concrete\[J]. Building Science and Technology, 2009, 21(2): 3-6. https://doi.org/10.3969/j.issn.1007-046X.2009.02.001. (In Chinese).



\[57] S. Li. Study on performance and classification method of recycled cement concrete coarse aggregate\[D]. Beijing University of Technology, 2009. (In Chinese).



\[58] T. Wang. Experimental study on strengthening of recycled aggregate and basic mechanical properties of recycled concrete\[D]. Shandong University of Science and Technology, 2009. (In Chinese).



\[59] H. Ye. Experimental study on mechanical properties and durability of high-quality recycled aggregate concrete\[D]. Zhejiang University of Technology, 2009. (In Chinese).



\[60] Y. Li. Experimental study on performance of recycled aggregate concrete\[D]. Chongqing University, 2009. (In Chinese).



\[61] J.L. Zhao. Study on basic properties of recycled concrete\[D]. Xi'an University of Architecture and Technology, 2009. (In Chinese).



\[62] C.L. Qiu. Study on recycled concrete and mechanical performance analysis of recycled concrete-filled steel tubular stub columns\[D]. Southwest Jiaotong University, 2009. (In Chinese).



\[63] L.L. Zhang. Experimental study on material properties of recycled concrete\[D]. Hefei University of Technology, 2009. (In Chinese).



\[64] C. Jin. Experimental study on mechanical property indexes of recycled concrete\[D]. Wuhan University of Technology, 2008. (In Chinese).



\[65] W. Zhang. Study on performance of recycled concrete\[D]. Kunming University of Science and Technology, 2008. (In Chinese).



\[66] L.S. Li, A.M. Gong, Y.L. Peng, et al. Application and research of fly ash in recycled concrete\[J]. Journal of Yunnan Agricultural University (Natural Science), 2009, 24(4): 597-602. https://doi.org/10.3969/j.issn.1004-390X.2009.04.022. (In Chinese).



\[67] T. Huang, X.Q. Peng, K.Y. Wang, et al. Influence of recycled coarse aggregates from different sources on performance of recycled concrete\[C]//Proceedings of the National Symposium on Resource Utilization of Solid Waste from Earthquake-Stricken Areas and Construction of Energy-Saving and Earthquake-Resistant Houses. 2009: 298-303. (In Chinese).



\[68] J. Pang. Experimental study on mechanical performance of recycled aggregate concrete\[D]. Chang'an University, 2010. (In Chinese).



\[69] J.H. Zhou, H.J. He, X.H. Meng, et al. Experimental study on basic mechanical properties of recycled concrete\[J]. Journal of Shenyang Jianzhu University (Natural Science), 2010, 26(3): 464-468. (In Chinese).



\[70] J. Ma, Z.B. Wang, J. Wang. Experimental study on compressive strength of recycled concrete\[J]. Journal of Huaiyin Institute of Technology, 2010, 19(3): 54-58. https://doi.org/10.3969/j.issn.1009-7961.2010.03.013. (In Chinese).



\[71] N. Jiang, Q. Xu, W. Zhang. Influence of recycled aggregate content on performance and strength of recycled concrete\[J]. Science Technology and Engineering, 2010, 10(19): 4843-4847. https://doi.org/10.3969/j.issn.1671-1815.2010.19.058. (In Chinese).



\[72] A.J. Chen, L.Y. Pan, J. Wang, et al. Study on influence of fly ash on performance of recycled concrete\[J]. Concrete, 2010(8): 84-87. https://doi.org/10.3969/j.issn.1002-3550.2010.08.029. (In Chinese).



\[73] L. Zhu. Performance evaluation of recycled coarse aggregate and study on early-age performance of recycled concrete\[D]. Nanjing University of Aeronautics and Astronautics, 2011. (In Chinese).



\[74] C. Gao, H.Z. Chen, Z.L. Song, et al. Experimental study on mechanical properties of recycled concrete aggregate\[J]. Journal of Liaoning Technical University (Natural Science), 2011, 30(S1): 81-84. https://doi.org/10.3969/j.issn.1008-0562.2011.z1.023. (In Chinese).



\[75] M.H. Zhou, L.J. Li. Experimental study and analysis on strength of recycled aggregate concrete\[J]. Concrete, 2011(5): 99-101. https://doi.org/10.3969/j.issn.1002-3550.2011.05.034. (In Chinese).



\[76] J.H. Liu. Experimental study on influencing factors of mechanical properties of recycled coarse aggregate concrete\[D]. Inner Mongolia Agricultural University, 2011. (In Chinese).



\[77] S.L. Wang, Y. Yu, B. Zhang, et al. Experimental study on influence of fly ash and silica fume on mechanical properties of recycled concrete\[J]. Concrete, 2011(12): 53-55. https://doi.org/10.3969/j.issn.1002-3550.2011.12.016. (In Chinese).



\[78] J. Ma, Z.B. Wang. Study on basic properties of recycled concrete\[J]. China Concrete and Cement Products, 2012(3): 18-21. https://doi.org/10.3969/j.issn.1000-4637.2012.03.005. (In Chinese).



\[79] S. Gu, T. Lei, J.L. Tao. Mix proportion design and early-age strength experimental study of recycled concrete\[J]. Industrial Construction, 2012, 42(4): 1-4. https://doi.org/10.13204/j.gyjz2012.04.002. (In Chinese).



\[80] J.F. Lu. Study on basic mechanical properties and micromechanism of recycled concrete\[D]. Guangxi University, 2013. (In Chinese).



\[81] H.B. Zheng. Study on influence of recycled coarse aggregate pretreatment on slump loss and basic mechanical properties of recycled concrete\[D]. Fuzhou University, 2012. (In Chinese).



\[82] M.M. Mao. Experimental study on performance of recycled coarse aggregate concrete\[D]. Hebei University of Engineering, 2012. (In Chinese).



\[83] Z.H. Du. Study on mechanical performance of construction waste recycled aggregate concrete and components\[D]. Zhengzhou University, 2012. (In Chinese).



\[84] Y. Zhang, X.J. Tang, X.H. Wang. Experimental study on slump and compressive strength of recycled coarse aggregate concrete and damage analysis\[J]. Journal of Yan'an University (Natural Science Edition), 2025, 44(3): 20-26. (In Chinese).



\[85] H.M. Qin. Experimental study on mechanical properties and durability of fly ash-slag composite recycled concrete\[J]. Jiangxi Building Materials, 2024(9): 33-35. (In Chinese).



\[86] D. Zhu, L. Huo, J.S. Feng, et al. Analysis on influence of recycled aggregate replacement rate on performance of recycled concrete\[J]. Shanxi Architecture, 2016, 42(31): 117-119. https://doi.org/10.3969/j.issn.1009-6825.2016.31.062. (In Chinese).



\[87] S.H. Lv, C.T. Yu, X.Z. Zhou, et al. Recycled coarse aggregate and its influence on performance of recycled concrete\[J]. Brick-Tile, 2017(8): 20-22. https://doi.org/10.16001/j.cnki.1001-6945.2017.08.004. (In Chinese).



\[88] T. Li, S.L. Wang. Experimental study on influence of recycled coarse aggregate with different service years on compressive performance of concrete\[J]. Concrete, 2017(8): 62-65. https://doi.org/10.3969/j.issn.1002-3550.2017.08.015. (In Chinese).



\[89] M.L. Yao, B.Y. Rao, Z. Chen, et al. Experimental study on influence of fly ash on compressive performance of recycled aggregate concrete\[J]. Cement Engineering, 2017(3): 86-88. https://doi.org/10.13697/j.cnki.32-1449/tu.2017.03.034. (In Chinese).



\[90] J.G. Sun, B.B. Xu, Y.L. Gu. Experimental study on performance of recycled concrete with high-volume fly ash\[J]. Concrete, 2016(2): 96-98. https://doi.org/10.3969/j.issn.1002-3550.2016.02.023. (In Chinese).



\[91] X.F. Wang, Q.Y. Li, J.L. Luo, et al. Mechanical properties of recycled coarse aggregate concrete with different qualities and fitting of Bolomey formula\[J]. Concrete, 2016(3): 60-64. https://doi.org/10.3969/j.issn.1002-3550.2016.03.015. (In Chinese).



\[92] J.G. Sun, Y.L. Gu. Analysis on influence of water-binder ratio and recycled coarse aggregate replacement rate on concrete performance\[J]. Concrete, 2016(4): 64-67. https://doi.org/10.3969/j.issn.1002-3550.2016.04.018. (In Chinese).



\[93] J. Zhao, J.C. Song, H.T. Yu, et al. Influence of different replacement ratios of construction waste recycled coarse aggregate on performance of recycled concrete\[J]. Guangdong Building Materials, 2016(7): 14-16. https://doi.org/10.3969/j.issn.1009-4806.2016.07.006. (In Chinese).



\[94] J.G. Chen, X.Z. Ling. Experimental study on mix proportion of recycled concrete with high-volume fly ash\[J]. Fly Ash Comprehensive Utilization, 2016(4): 14-17,20. https://doi.org/10.3969/j.issn.1005-8249.2016.04.004. (In Chinese).



\[95] L. Yan, J. Yu. Mechanical properties of recycled coarse aggregate concrete with different replacement rates\[J]. Shanxi Architecture, 2016, 42(25): 110-111,188. https://doi.org/10.3969/j.issn.1009-6825.2016.25.059. (In Chinese).



\[96] J. Yu, R. Liang, Y.J. Qin. Experimental study on performance of C30 recycled coarse aggregate concrete\[J]. Building Science, 2015, 31(1): 59-63. https://doi.org/10.13614/j.cnki.11-1962/tu.2015.01.012. (In Chinese).



\[97] B. Hu, T.H. Chai. Influence and analysis of replacement rate on performance of recycled aggregate concrete\[J]. Jiangxi Building Materials, 2015(6): 5-6. https://doi.org/10.3969/j.issn.1006-2890.2015.06.005. (In Chinese).



\[98] J.M. Dong, K. Wang, X.B. Xu, et al. Experimental study on physical and mechanical properties of recycled concrete\[J]. China Concrete, 2015(4): 60-62. https://doi.org/10.3969/j.issn.1674-7011.2015.04.011. (In Chinese).



\[99] X.F. Wang, Q.Y. Li, J.L. Luo, et al. Influence of quality and replacement rate of recycled coarse aggregate on compressive strength of recycled concrete\[J]. China Concrete and Cement Products, 2015(5): 85-88. https://doi.org/10.3969/j.issn.1000-4637.2015.05.023. (In Chinese).



\[100] X.W. Deng. Compressive strength test results and analysis of recycled coarse aggregate concrete\[J]. Science \& Technology Information, 2015(16): 59-60. https://doi.org/10.3969/j.issn.1672-3791.2015.16.031. (In Chinese).



\[101] P. Li, M.L. Li. Study on compressive strength of recycled concrete with different replacement rates\[J]. Sichuan Building Materials, 2015, 41(4): 12-14. https://doi.org/10.3969/j.issn.1672-4011.2015.04.007. (In Chinese).



\[102] M.J. Zhang, J.K. Zhao, Z. Ding. Study on performance of recycled aggregate concrete\[J]. China Powder Science and Technology, 2015, 21(4): 85-88. https://doi.org/10.13732/j.issn.1008-5548.2015.04.019. (In Chinese).



\[103] J.H. Chen. Influence of recycled aggregate on basic properties of recycled concrete\[J]. Journal of Changsha University, 2015(5): 29-31. https://doi.org/10.3969/j.issn.1008-4681.2015.05.009. (In Chinese).



\[104] B.G. Luo, H.Y. Qin. Influence of mineral admixtures on mechanical properties of recycled concrete\[J]. Journal of China \& Foreign Highway, 2014, 34(2): 268-273. https://doi.org/10.3969/j.issn.1671-2579.2014.02.064. (In Chinese).



\[105] J.F. Yuan, W. Wang, Y.T. Lu. Experimental study on influence of water-binder ratio and recycled coarse aggregate replacement rate on strength of recycled concrete\[J]. Chongqing Architecture, 2014(10): 53-55. https://doi.org/10.3969/j.issn.1671-9107.2014.10.053. (In Chinese).



\[106] L. Suo, P. Peng, B. Tian. Experimental study on workability and compressive strength of recycled concrete\[J]. Journal of Civil Engineering and Management, 2014(3): 39-42,46. https://doi.org/10.3969/j.issn.2095-0985.2014.03.008. (In Chinese).



\[107] X.F. Tong, D.Y. Yang, X. Wang, et al. Study on basic properties of fly ash recycled concrete\[J]. Concrete, 2014(7): 27-31. https://doi.org/10.3969/j.issn.1002-3550.2014.07.008. (In Chinese).



\[108] T. Ye, Y.H. Xu, J. Zhang. Experimental study on compressive strength of recycled concrete based on workability\[J]. Building Structure, 2014, 44(21): 75-77,66. https://doi.org/10.19701/j.jzjg.2014.21.016. (In Chinese).



\[109] H.T. Yang, S.Z. Tian. Study on preparation and performance of high-strength recycled aggregate concrete\[J]. Journal of Functional Materials, 2013, 44(17): 2524-2527. https://doi.org/10.3969/j.issn.1001-9731.2013.17.020. (In Chinese).



\[110] Y.L. Hou, G. Zheng. Mechanical properties of recycled aggregate concrete at different ages\[J]. Journal of Building Materials, 2013, 16(4): 683-687. https://doi.org/10.3969/j.issn.1007-9629.2013.04.023. (In Chinese).



\[111] Z.S. Wang. Study on mechanical properties and calculation methods of recycled concrete\[J]. Sichuan Building Science, 2013, 39(5): 238-242. https://doi.org/10.3969/j.issn.1008-1933.2013.05.056. (In Chinese).



\[112] X.W. Huang. Experimental study on size effect of compressive strength of recycled coarse aggregate concrete\[J]. Fujian Construction Science \& Technology, 2024(4): 74-77. (In Chinese).



\[113] Z.X. Xing, Y.N. Zhou. Study on basic properties of recycled concrete\[J]. Journal of North China University of Water Resources and Electric Power (Natural Science Edition), 1998(2): 30-32. (In Chinese).



\[114] Y.F. Ma, X.Y. Xu. Experimental study on compressive performance of recycled concrete\[J]. Jiangsu Building Materials, 2010(1): 21-24. https://doi.org/10.3969/j.issn.1004-5538.2010.01.007. (In Chinese).



\[115] G.F. Mao. Experimental study on recycled coarse aggregate concrete\[D]. Qingdao University of Technology, 2008. (In Chinese).



\[116] Y.X. Guo. Study on mix proportion design method of recycled concrete based on quality and replacement rate of recycled aggregate\[D]. Qingdao University of Technology, 2018. (In Chinese).



\[117] J. Cao, J. Zhang, Q.Y. Li. Influence of mineral admixtures and recycled aggregate on workability of recycled concrete\[J]. Journal of Qingdao University of Technology, 2009, 30(4): 140-144,165. https://doi.org/10.3969/j.issn.1673-4602.2009.04.029. (In Chinese).



\[118] Y.J. Qin, Z.K. Qi, C. Luo. Preliminary experimental analysis on factors influencing workability of recycled concrete\[J]. Concrete, 2012(2): 81-82,85. https://doi.org/10.3969/j.issn.1002-3550.2012.02.025. (In Chinese).



\[119] Y.L. Sun, X.H. Liao, Y. Li. Prediction of slump of recycled concrete\[J]. Concrete, 2013(6): 81-83,96. https://doi.org/10.3969/j.issn.1002-3550.2013.06.023. (In Chinese).

