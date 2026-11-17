from common import *
def main():
    refs=pd.read_csv(data_file('new_references.csv')).set_index('ref_no');focus=pd.read_csv(data_file('focus_records.csv'))
    urls={36:'https://doi.org/10.3969/j.issn.1003-8825.2007.04.052',82:'',109:'https://www.gncl.cn/CN/Y2013/V44/I17/31',8:'https://pubs.cstam.org.cn/article/id/628b6a66ca140b06b8e0ad43',9:'https://doi.org/10.3969/j.issn.1002-3550.2018.11.015',52:'https://sylx.ustc.edu.cn/sylx/article/issue/2021_36_6',77:'https://lwtj.shzu.edu.cn/openfile?dbid=72&lwsing=27a63aaee7662ddad219bb00f8cffee5&objid=54_56_54_48_50'}
    notes={36:'原文未获取；不能由高强样本及模型低覆盖推断龄期或标签错误',82:'未获取河北工程大学该学位论文原文；中文作者名和精确题名也未独立确认',109:'官方摘要确认作者/题名及0/30/50/80/100%再生替代试验设计；未获取方法和逐行数值表',8:'仅找到孟红2012同主题学位论文的下游引文，不能代替附件所列会议论文',9:'附件及下游引文指向2018预测建模研究，原始实验或二次汇编映射未知',52:'官方期刊目录确认橡胶集料/钢管约束研究范围；不能仅凭题名认定30条数据库混合物错误',77:'下游公开学位论文引文支持题名涉及粉煤灰与硅粉；未确定附件8行是否仅选无硅粉子集'}
    fields=[];summary=[]
    for ref in REFS:
        d=focus[focus.ref_no==ref];r=refs.loc[ref]
        summary.append(dict(ref_no=ref,records=len(d),first_record=d.record_id.iloc[0],last_record=d.record_id.iloc[-1],citation=r.citation,doi=r.doi,primary_fulltext_obtained=False,rowwise_original_confirmation=False,identity_status=('已证实（官方题名/作者）' if ref in [109,52] else '无法核实（附件或下游引文）'),overall='无法核实关键行级标签和配合比',url=urls[ref],note=notes[ref]))
        def add(field,status,value,basis,level='原文行级'):
            fields.append(dict(ref_no=ref,field=field,status=status,value=value,evidence_level=level,evidence_url=urls[ref],basis=basis))
        add('database_record_range','已证实',f'{len(d)}行; {d.record_id.iloc[0]}-{d.record_id.iloc[-1]}','附件数据库与Phase 2冻结副本逐字节一致','本地输入')
        add('bibliographic_identity','已证实' if ref in [109,52] else '无法核实',r.citation,notes[ref],'官方元数据' if ref in [109,52] else '附件/二手线索')
        add('experiment_or_recompiled_origin','无法核实','unknown',notes[ref])
        add('specimen_shape_size','无法核实','unknown','未得到该来源方法章节；不从编库等效150mm声明反推原始试件')
        add('age_28days','无法核实','28days_curator_claim_only','README称统一28天，未获得该来源逐行独立龄期证据','编库声明')
        add('strength_definition','无法核实','150mm_cube_equivalent_curator_claim','原始立方体/圆柱/轴压/约束强度及数据库目标映射未核实','编库声明')
        add('strength_unit','已证实' if ref==109 else '无法核实','MPa_abstract' if ref==109 else 'MPa_curator_claim','官方摘要采用MPa量纲但未绑定逐行28天强度' if ref==109 else '附件单位MPa已读，原文该列未独立确认','官方摘要' if ref==109 else '编库声明')
        add('test_standard','无法核实','unknown','未见原始测试标准和版本，不推定GB/ASTM/EN')
        add('conversion_factor','无法核实','unknown','编库未附逐行原始尺寸及换算系数；不自行换算')
        add('mixture_row_mapping','无法核实','unknown','没有可用原文配合比/响应表完成逐行映射；原始剂量另存focus_records.csv')
        if ref==109:
            expected={0,30,50,80,100};assert set(d.rar)==expected
            add('replacement_design','已证实','0/30/50/80/100%','官方摘要设计替代水平与附件此来源RAR集合一致，不等于全部剂量/响应逐行验证','官方摘要+本地集合')
            add('bibliographic_pages','存在冲突','publisher_page:31-0; supplied_reference:2524-2527','官方页面显示页码与附件不一致，可能为站点元数据问题；不据此判定实验值错误','官方网页与附件')
    save(summary,'source_verification_summary.csv');save(fields,'source_field_evidence.csv')
    attempts=[
      (36,'索引/题名定位','DOI和路基工程2007/105-107以及Lu/Ye英文引文检索','未获得对应原文URL'),(36,'DOI入口',urls[36],'公开入口不可读取'),
      (82,'学位论文索引定位','英文引文、中文题名及河北工程大学2012/毛/再生组合','未定位可核实的原始论文全文'),
      (109,'官方期刊入口',urls[109],'题名作者和摘要可见；真实PDF未取得，HTTP读取失败/超时，浏览器入口超时'),(109,'DOI规范入口','https://www.gncl.cn/CN/10.3969/j.issn.1001-9731.2013.17.020','不可读取'),
      (8,'会议/作者题名定位','Meng/Li 2012 BP网络及孟红李秋义题名检索','未获取会议原文'),(8,'下游学术引文',urls[8],'定位到同主题硕士论文引文，文献类型不同，不能替代'),
      (9,'索引/题名定位','Gao2018/58-61与中文深度学习强度预测题名','无原始实验表可核查'),
      (52,'官方期刊目录',urls[52],'确认题名/作者/研究对象，未取得全文表'),(52,'官方DOI全文入口','https://sylx.ustc.edu.cn/sylx/article/doi/10.7520/1001-4888-20-244','不可读取'),(52,'学会期刊入口','https://pubs.cstam.org.cn/article/doi/10.7520/1001-4888-20-244','不可读取'),
      (77,'DOI入口','https://doi.org/10.3969/j.issn.1002-3550.2011.12.016','不可读取'),(77,'题名与下游引文',urls[77],'下游公开论文参考文献支持书目信息，未取得原文')]
    save([dict(ref_no=a,route=b,query_or_url=c,outcome=d,date='2026-11-08') for a,b,c,d in attempts],'source_access_log.csv')
    candidates=[
      ('C1','Predicting compressive strength of recycled aggregate concrete using AI with experimental validation','10.1007/s43503-026-00111-y','https://link.springer.com/article/10.1007/s43503-026-00111-y','原文公开：25个实测配合比，1125为扩增记录；28天150mm立方体','LA abrasion与所需CV不同；11输入完整映射未建立，且含再生细骨料','not_qualified_input_mapping'),
      ('C2','Dataset and Python Codes for Data-Driven Identification of Mechanical Performance Thresholds and Transition Regions in RAC','10.5281/zenodo.21758923','https://zenodo.org/records/21758923','编译数据库，说明侧重归一化性能，文件下载未取得','11输入、原始MPa标签和文献独立性未能核实','unknown_not_admitted'),
      ('C3','Recycled aggregate concrete mix design and testing results','','https://b2find.eudat.eu/dataset/3d45d5d1-578b-5a24-873f-3be6a7a29293','索引发现记录，原入口429，未获取原始数组','原始来源、11输入和试件口径均未核实','unknown_not_admitted'),
      ('C4','Fresh physical and mechanical performance of pre-soaked RCA concrete','10.17515/resm2026-2293me0904rs','https://jresm.org/article/resm2026-2293me0904rs/','官方摘要：5替代水平，7/28天；PDF入口无法读取','摘要的混凝土密度/吸水率不得替代RCA性质；尺寸/CV及逐条剂量未核实','unknown_not_admitted'),
      ('C5','Confined Crushing of Recycled Concrete Aggregate: Fractal Gradation Loose-Bulk-Density Response and Mix-Specific Concrete Use','','https://www.sciencedirect.com/science/article/pii/S2590123026033773','索引摘要：单一全再生混凝土配方，28天150mm等效强度','样本只有一个配方；松散堆积密度不可替代表观密度，CV/完整输入未核实','not_qualified_scope_and_mapping'),
      ('C6','Eco-Friendly Concrete Using Recycled Aggregates from Excavation Construction and Demolition Waste','10.3390/buildings16081576','https://www.mdpi.com/2075-5309/16/8/1576','官方索引摘要：6种实验混凝土、150mm立方体；全文入口429','RCA表观密度/CV/吸水率及28天行级对应未建立','unknown_not_admitted')]
    allold=pd.read_csv(data_file('old_all980_classification.csv'));known=set(refs.source_id)|set(allold.source_id)
    screen=[]
    for cid,title,doi,url,observed,reason,status in candidates:
        screen.append(dict(candidate=cid,title=title,doi=doi,url=url,observed=observed,not_admitted_reason=reason,decision=status,known_publication_doi_overlap=('yes' if doi in known else 'not_detected' if doi else 'unknown'),experiment_reuse_overlap='unknown',recipe_overlap='not_tested_no_compatible_rows',rows_admitted=0))
    save(screen,'independent_candidates.csv')
    novelty=[
      ('L1','Reliable Compressive Strength Prediction of Self-Compacting Concrete with Recycled Coarse Aggregate Using an Interpretable Machine Learning Model with Uncertainty Quantification','2026-07-23','peer_reviewed','https://www.mdpi.com/2504-477X/10/8/379','RAC重复/矛盾配方、来源外推下降、split-conformal和CQR均已有','不能声称首次RAC来源失效或首次自适应区间','本数据库115出版来源/99关联组中的区间成本和源消失的定量证据','高'),
      ('L2','Heterogeneity-aware stacked machine learning for predicting high-performance concrete compressive strength','2026-04-07','peer_reviewed','https://doi.org/10.3389/fbuil.2026.1790749','多来源HPC分组验证及异质性已研究','按来源划分本身不是创新','RAC来源关联图下的来源等权区间与拒判服务范围','中'),
      ('L3','Evaluating external generalizability of machine learning models for recycled aggregate concrete property prediction','2024','peer_reviewed_abstract_verified','https://www.sciencedirect.com/science/article/pii/S0959652624026155','RAC外部泛化与内部分数的权衡已有报道','外推分数下降不是新结论','在既有泛化问题上分析校准/评分/来源保留','高'),
      ('L4','Distributional shift safety margin for machine learning models in structural engineering','2026-07-18','peer_reviewed','https://doi.org/10.1007/s42452-026-09140-9','普通混凝土UCI等任务上的无标签偏移代理与安全代价','不能声称首次距离风险或首次混凝土偏移保障','自然出版来源隔离，而非人为协变量扰动；不提出保障方法','中'),
      ('L5','Benchmarking uncertainty quantification for engineering regression under graded distribution shift','2026-10-26','preprint_not_peer_reviewed','https://arxiv.org/abs/2610.35356','包含Concrete的偏移、子群覆盖、宽度和高拒判代价','拒判可隐藏大范围无服务和困难偏移失败已有直接先例','RAC出版来源单位的消失台账及固定来源分母的定量评估','高'),
      ('L6','Selective Prediction Intervals: Jointly Learning to Predict Bound and Abstain','2026-11-04','preprint_not_peer_reviewed','https://arxiv.org/abs/2611.06158','含Concrete基准，固定预测器下联合区间评分和拒判、宽度排序的局限','不得将区间评分加拒判视为首创，也不声称joint优胜','不训练新门控；比较简单规则对出版来源覆盖服务的影响','高'),
      ('L7','Selective Regression under Fairness Criteria','2022','peer_reviewed','https://proceedings.mlr.press/v162/shah22a.html','选择性回归不同群体风险可以不同','来源/群体代价的概念不是新理论','具体RAC数据、来源关联与失服务计量','高'),
      ('L8','Reliable cross-laboratory prediction intervals for concrete compressive strength under distribution shift','2026-12 issue; online_first_unknown','future_issue_date_not_counted_as_established_prior','https://www.techno-press.com/papers/22627','网页可访问但卷期晚于本次截止日，未确认首发日期','仅作为前瞻重叠风险，不据此宣称截至11月8日已正式发表','不用于改变已有评价或提出算法；后续写作需核对时间','待定')]
    save([dict(id=a,title=b,date=c,publication_status=d,url=e,already_addressed=f,prohibited_novelty_claim=g,current_dataset_increment=h,overlap_risk=i) for a,b,c,d,e,f,g,h,i in novelty],'novelty_matrix.csv')
    queries=['recycled aggregate concrete dataset density crushing 2026','recycled aggregate concrete 28 150 absorption 2025 experimental','site:data.mendeley.com recycled aggregate concrete compressive strength','site:zenodo.org recycled aggregate concrete dataset','site:data.mendeley.com recycled aggregate 2026 strength','recycled aggregate concrete experiment 150 cube density crushing absorption 2026','recycled aggregate concrete dataset figshare 2025 compressive source','recycled aggregate concrete experimental dataset Zenodo 28 day mix 2026']
    topics=['recycled aggregate concrete conformal 2026','concrete compressive strength distribution shift 2026','concrete selective prediction regression uncertainty','recycled aggregate concrete source generalization uncertainty calibration','recycled aggregate concrete selective conformal 2026','concrete distribution shift source conformal 2026']
    save([dict(track='independent_data',index=i+1,query=q,provider='public_web_search',cutoff='2026-11-08',scope='discovery_only_followup_pages_logged_in_screening') for i,q in enumerate(queries)]+[dict(track='novelty',index=i+1,query=q,provider='public_web_search',cutoff='2026-11-08',scope='peer_reviewed_and_preprints_separated') for i,q in enumerate(topics)],'bounded_search_log.csv')
    note=dict(independent_search_queries=8,independent_candidates=6,rows_admitted=0,external_confirmation_performed=False,search_closed=True,novelty_queries=6,focus_sources=7,focus_rows=247,focus_primary_fulltexts_obtained=0,focus_rowwise_confirmed_sources=0,confirmed_numeric_conflict_sources=0,confirmed_bibliographic_page_conflicts=1,important='No full-text row mapping is not evidence the records are wrong')
    (OUT/'evidence_summary.json').write_text(json.dumps(note,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(note,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
