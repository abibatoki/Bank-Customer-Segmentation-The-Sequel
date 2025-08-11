# Bank Customer Segmentation – The Sequel

This project continues the work from **(https://github.com/abibatoki/Bank-Customer-Segmentation)**, where I grouped banking customers into segments based on their behavior patterns and value to the business. This sequel transforms those insights into an interactive dashboard that enables anyone to dynamically explore the segmentation results.

---

## 🚀 Live Demo

View it here:  
🔗 **(https://huggingface.co/spaces/abibatoki/indian_bank_customer_segmentation_dashboard)**


---

## 📌 Project Overview
The goal is to make customer segmentation results easier to explore and interpret by:

- Presenting the data visually through a clean, interactive interface.
- Allowing city-by-city exploration of customer behavior.
- Providing quick access to segment definitions and business interpretations.

This approach makes it possible to see the local variations in customer engagement, spending, and loyalty.

---

## 🔍 Key Features
- **City Profiles:** Normalized frequency, spending, and recency metrics for each location.
- **Customer Distribution:** View how segments are spread across different cities.
- **Segment Positioning:** Bubble chart showing segment relationships in terms of frequency vs. spending.
- **Executive Summary:** Clear, concise descriptions of each segment for quick decision-making.

---

## 📊 Cluster Interpretations

### 🧮 1. Average Total Spend by Cluster and City (Top 20 Cities)

<img width="4753" height="1756" alt="avgspend_by_cluster_city" src="https://github.com/user-attachments/assets/c83cfd49-795d-474d-979e-280723bc3640" />

**💡 Insight:**
- Cluster 2 consistently records the highest average total spend across all major cities.  
- Clusters 1 and 3 are generally on the lower end of spending, with Cluster 0 consistently lowest.  
- This pattern remains stable across cities, showing little variation in average spend within clusters.  

**🔍 Why does this happen?**
- Transaction amounts are fairly uniform across the dataset.  
- Frequency and AvgMonetary are the main contributors to TotalMonetary, and clustering was based on scaled RFM features.  
- Clustering enforces consistency in monetary behavior per segment regardless of geography.  

**🎯 So What:**
- Clusters are a reliable predictor of spend potential, regardless of city.  
- Cluster 2 customers are High-Value Spenders → target with exclusive offers, upgrades, and retention plans.  

---

### 👥 2. Customer Distribution by Cluster and City (Top 20 Cities)

<img width="4753" height="1756" alt="distribution_by_cluster_city" src="https://github.com/user-attachments/assets/ca583206-6b05-49fe-8abd-bf18ddfe4704" />

**💡 Insight:**
- Cluster 3 dominates the customer base in most cities, representing the largest group.  
- Cluster 2 (top spenders) is smaller but present in all cities.  
- Cities like Mumbai, New Delhi, Gurgaon, and Bangalore show diverse cluster representation.  

**🎯 So What:**
- Cluster 3 → huge opportunity for re-engagement through personalized offers.  
- Cluster 2 → prioritize for premium loyalty programs.  
- All clusters across cities → supports location-specific, cluster-aware marketing.  

---

### 🗺️ Heatmap Interpretation: Customer Volume by City and Cluster

<img width="3364" height="2354" alt="volume_by_cluster_city" src="https://github.com/user-attachments/assets/33736daa-f87f-4eb3-a279-67a13ee688dd" />

**💡 What it shows:**
- Each cell = number of customers from a specific city–cluster combination.  
- Deeper red = higher count, deeper blue = lower count.  

**🔎 Key Business Insights:**
1. **Cluster 3 dominates in major metro areas**  
   - Mumbai (34,001), New Delhi (25,423), Gurgaon (22,230), Bangalore (24,028).  
   - Largest segment, often mid-tier or at-risk customers → reactivation potential.  
   - **📌 Implication:** Great for loyalty and upsell campaigns.

2. **High-value Cluster 2 customers are more concentrated**  
   - Strong presence in Delhi, Bangalore, Chennai, Mumbai.  
   - **📌 Implication:** Ideal hubs for premium services and exclusive offers.

3. **Emerging clusters in second-tier cities**  
   - Noida, Faridabad, Kolkata, Pune → balanced representation of multiple clusters.  
   - **📌 Implication:** Ideal for localized promotions and pilot campaigns.

---

### 🎯 Strategic Takeaways for the Business

| Opportunity | Action |
|-------------|--------|
| High population in Cluster 3 across metros | Launch broad re-engagement or loyalty point revival campaigns |
| Cluster 2 present in all major cities | Offer exclusive financial products, personalized rewards |
| Balanced segments in Tier-2 cities | Test localized promotions, build regional engagement playbooks |

---

## 🛠️ Code and Resources Used
- **Python Version:** 3.8
- **Libraries:**
  - Streamlit
  - Pandas, NumPy
  - Plotly Express, Matplotlib
