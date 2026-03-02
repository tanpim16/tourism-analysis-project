# ✈️ Analyzing the Impact of Secondary City Tourism on Real Income Generation for Local Communities in Thailand during 2023 - 2025

## **Data Source**
1. Tourism Revenue Data (2023 - 2025): https://www.mots.go.th/news/category/411
2. Consumer Price Index (CPI) Data (2023 - 2025): https://index.tpso.go.th/document/cpip/post-month
3. API of Google Trends Data (2023 - 2025): Search keywords such as "travel + province" (e.g., "travel + province name").

---

## **Objectives** ##

This section presents data-driven insights derived from static visual analytics examining tourism expansion, redistribution effects, income quality, and real income generation across Thailand’s primary and secondary cities. Each figure represents an analytical step designed to translate tourism data into interpretable economic insights.

---

## **Research Questions** ##
This study addresses the following research questions:
1. Do secondary cities experience higher tourist growth rates than primary destinations during 2023–2025?
2. Has tourism policy contributed to the redistribution of tourists toward secondary cities?
3. Does tourism development improve income quality, measured by revenue per tourist and international visitor share?
4. Can online search interest predict tourism demand and tourism revenue?
5. Does tourism growth generate real income gains for local communities after adjusting for inflation?

---

## **Introduction** ##

Tourism is one of the most important drivers of Thailand’s economy, contributing significantly to national income, employment, and regional economic activity. Tourism revenue accounts for a substantial share of Thailand’s gross domestic product and plays a key role in supporting economic recovery through foreign exchange earnings and service-sector employment (World Bank, 2023). In addition to its direct contribution, tourism generates multiplier effects across related industries such as transportation, accommodation, food services, and local enterprises, thereby supporting community livelihoods and regional development (Lloyds Bank, 2024).

However, tourism development in Thailand has historically been concentrated in major destinations, leading to unequal distribution of economic benefits across regions. To reduce regional disparities, the Thai government introduced the secondary-city tourism policy, aiming to redistribute tourist flows toward lesser-visited provinces and promote inclusive local economic growth through community-based tourism and regional promotion strategies (Chulalongkorn University, 2020).

Despite increasing tourism promotion and visitor growth in secondary cities, it remains unclear whether tourism expansion translates into real economic improvement for local communities. Increased tourist arrivals may not necessarily lead to higher real income if benefits are unevenly distributed or offset by rising living costs. Therefore, this study examines whether secondary-city tourism contributes to real income generation and more balanced regional development in Thailand.

---
## **1. Tourism Expansion: Growth Comparison** ##

### **Tourism Trends** ###

Tourism represents an important source of economic activity across provinces in Thailand, although its contribution may differ between primary and secondary destinations. While primary cities have traditionally served as established tourism centers, secondary cities have increasingly been promoted as alternative destinations under national tourism policies. 

Examining trends in tourism performance across these two groups is therefore important for identifying emerging patterns and assesing the potential for broader tourism development. Observing changes in both tourist arrivals and tourism income over time allows for an evaluation of whether growth in secondary cities signals expanding economic opportunities and increasing participation in the tourism economy. By comparing these trends, the analysis provides insight into how tourism dynamics evolve across provinces and helps reveal the potential for secondary destinations to strengthen their economic role within Thailand’s tourism sector.

### **Figure 1: Monthly Tourist Arrivals Trend**
![Figure 1](visualizations/total_visitors_trend.png)

The comparison of visitor arrivals (Figure 1A) reveals a promising shift in travel behavior:
* **Success in Redistribution**: Secondary cities are showing a steady and reliable growth trend that mirrors the seasonal patterns of major hubs, particularly during the year-end "High Season."
* **The Milestones**: Major cities continue to lead, reaching a massive peak of **21.9 million visitors** in December 2024. Meanwhile, secondary cities proved their potential by climbing to a peak of **11.2 million** in December 2025.
* **Key Insight**: National policies are effectively moving the needle in terms of volume, as more travelers explore beyond traditional destinations.

### **Figure 2: Monthly Tourism Income Trend (Nominal)**
![Figure 2](visualizations/total_revenue_trend.png)

While more people are traveling, a closer look at the revenue (Figure 2) reveals a different story:
* **Revenue Disparity**: Despite having roughly half the visitor volume of major cities, secondary cities generate only a fraction of the total income.
* **Peak Comparison**: Major cities captured a peak of **248K Million THB** (approximately 248 Billion THB), whereas secondary cities reached an income peak of approximately **35K Million THB**.
* **The Spending Gap**: Correlation of the data shows that average spending per head in major cities remains approximately **3.6 times higher** than in secondary destinations.

## 💡 Conclusion & Strategic Implications
The results support the premise that Thailand’s secondary-city tourism policy has successfully stimulated tourist movement toward lesser-visited provinces. The similarity in seasonal patterns, as shown in **Figure 1A**, implies a stronger integration of secondary cities into national tourism demand.

However, the **weaker income response** highlighted in **Figure 2** indicates that increased visitor numbers alone do not guarantee equivalent economic benefits. Future development should focus on enhancing infrastructure and service quality in secondary destinations to convert high visitor volumes into sustainable local economic value.

---

## **2. Tourism Redistribution Toward Secondary Cities** ##

### **Figure 3: Annual Tourism Volume and Income in Secondary Cities**
![Figure 3](visualizations/Figure%203.png)

Figure 3 shows that tourism activity in secondary cities is expanding in terms of both visitor numbers and income, but not at the same pace. Total arrivals to secondary destinations increase steadily between 2023 and 2025, confirming that more travelers are being drawn beyond traditional primary hubs. However, the revenue line grows more slowly and with smaller peaks than visitor volume, indicating that each additional tourist in secondary cities generates less income on average compared with tourists in major cities. This divergence suggests that while redistribution policies are successfully shifting tourism volume toward secondary provinces, these areas still face structural constraints—such as lower spending per trip, limited high-value services, or weaker pricing power—that prevent visitor growth from translating fully into proportional economic gains for local communities.

### **Figure 4: Visitor Share of Secondary Cities in National Tourism**
![Figure 4](visualizations/Figure%204.png)

Figure 4 summarizes how tourism volume and income evolve in secondary cities over 2023–2025. The orange line shows the total number of visitors to all secondary cities combined, while the blue line tracks total tourism revenue generated in these destinations (in million THB).

This pattern provides visual evidence that tourism redistribution policies are working in terms of volume: more travelers are being redirected toward secondary provinces. However, when read together with Figure 2, the chart also suggests that this increased share of visitors does not yet translate into proportionate tourism income, highlighting a gap between successful redistribution of tourists and the depth of economic benefits captured locally.

### **Growth Dynamics and Expansion Patterns** ###

#Figure 5: Monthly year-over-year (YoY) Tourism Income Growth#
![Figure 5](visualizations/Figure%205.png)

The Year-over-Year (YoY) tourism income growth in 2025 shows a clear moderation following the strong expansion observed in 2024. Growth in primary cities declined from approximately 15.00%–30.00% in early 2024 to around 0.00% at the beginning of 2025, with several mid-year months recording negative growth between –5.00% and –10.00%, indicating slightly lower revenue compared with the corresponding months of the previous year.

In contrast, secondary cities maintained mostly positive YoY income growth throughout 2025, generally fluctuating between 3.00% and 10.00%, and exhibiting lower volatility than primary cities.

The decline in YoY growth in primary cities is largely attributable to a base-year effect, as elevated revenue levels in 2024 increased the comparison benchmark. Consequently, lower YoY values reflect a normalization of growth rather than a contraction in tourism activity. The results indicate differing growth dynamics, with primary cities entering a stabilization phase while secondary cities continue to demonstrate gradual expansion, emphasizing the importance of interpreting YoY indicators within broader time-series trends.


## Tourism Income and Contribution to Local Income Distribution ##

To evaluate the impact of inflation on tourism income, this study applies a real-value adjustment using the Consumer Price Index (CPI). Nominal tourism revenue is converted into real revenue by controlling for changes in price levels over time, allowing a comparison between observed income growth and actual purchasing power. This approach enables a clearer assessment of whether tourism growth translates into genuine income improvement across primary and secondary cities.

## Figure 6. Real Tourism Income Generation (CPI-Adjusted Revenue) ##

![Figure 6](visualizations/Figure%206.png)

Figure 6 presents CPI-adjusted (real) tourism revenue for major and secondary cities between 2023 and 2025. After controlling for inflation, the overall level of income generated by tourism remains substantially higher in primary destinations, but the upward trend in secondary cities becomes more meaningful: increases in revenue more clearly represent genuine gains in local purchasing power rather than price effects alone.

When read together with Figure 2 (nominal tourism income), Figure 6 helps reveal the "inflation illusion" in tourism-led development. Some of the rapid nominal revenue growth in primary cities is moderated once adjusted for CPI, while real revenue in secondary cities grows more steadily. This suggests that secondary-city tourism contributes to more gradual but tangible improvements in local real income, even though the absolute revenue gap with primary cities remains large.

### Reference ###
Chulalongkorn University. (2020). Tourism development and secondary city policy in Thailand (Master’s thesis). Chulalongkorn University Institutional Repository. https://digital.car.chula.ac.th/chulaetd/6448/

Lloyds Bank. (2024). Thailand: Economic context and market overview. Lloyds Bank Trade. https://www.lloydsbanktrade.com/en/market-potential/thailand/economical-context

World Bank. (2023, December 14). Thai economy to recover in 2024 driven by tourism and exports recovery. World Bank. https://www.worldbank.org/en/news/press-release/2023/12/14/thai-economy-to-recover-in-2024-driven-by-tourism-exports-recovery
