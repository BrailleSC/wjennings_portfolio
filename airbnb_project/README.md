**Airbnb Revenue Analysis (2016)**

This project explores the relationship between Airbnb listing features and yearly revenue using real-world data from 2016. By examining how factors such as beedrooms, bathrooms, and review scores impact a listing's yearly revenue, this analysis aims to give us a starting point for considerations when purchasing a property to rent out with Airbnb.


**Project Goals**

-Investigate key features influencing yearly revenue

-Visualize trends across bedroom and bathroom counts

-Build a linear regression model to quantify impact


**Revenue by Number of Bedrooms**

![Revenue by Bedrooms](Charts/revenue_bedrooms.png)

As expected, revenue generally increases with more bedrooms, with a notable jump in median earnings around 5-bedroom listings. Outliers with very high revenue exist in each category, likely due to luxury or frequently booked properties.


**Revenue by Number of Bathrooms**

![Revenue by Bathrooms](Charts/revenue_bathrooms.png)

Similar to bedroom count, more bathrooms tend to correlate with higher yearly revenue. Listings with 4+ bathrooms tend to perform particularly well, indicating a potential premium on larger, more accommodating spaces.


**Revenue by Review Scores**

![Revenue by Review Scores](Charts/revenue_reviews_scores.png)

Interestingly, review scores were not a strong or statistically significant factor in yearly revenue. While very low scores are rare, and slightly affect revenue, most listings cluster around the same revenue range regardless of ratings. A visible trend here is that there tend to be a lot of listings with ratings along the 60, 80, and 100 lines. Likely these have a low number of ratings which might be considered for exclusion. 


**Linear Regression Summary**

| Term                | Estimate | Std. Error | t-value | p-value | 95% CI (Lower) | 95% CI (Upper) |
|---------------------|----------|------------|---------|---------|----------------|----------------|
| (Intercept)         | -6,021   | 7,841      | -0.768  | 0.443   | -21,402        | 9,359          |
| Bedrooms            | **13,390**   | 862        | 15.5    | **< 2e-16** | 11,699         | 15,081         |
| Bathrooms           | **15,162**   | 1,279      | 11.9    | **< 2e-16** | 12,655         | 17,670         |
| Review Score Rating | 56.3     | 82.6       | 0.681   | 0.496   | -105           | 218            |


**Model Fit Metrics**
- **R-squared**: 0.311  
- **Adjusted R-squared**: 0.310  
- **Residual Std. Error**: 27,630 (on 2,311 DF)  
- **F-statistic**: 347.9 on 3 and 2,311 DF  
- **Overall model p-value**: < 2.2e-16


**Key Findings**

Bedrooms and bathrooms are both statistically significant predictors of revenue:

+
    +$13,390 per additional bedroom

+    +$15,162 per additional bathroom
+    (both p < 2e-16)

Review Score Rating, despite assumptions, is not statistically significant in the model. This may be due to:

  -Limited variation (most listings have high ratings).
  
  -Revenue being driven more by property features and availability than by marginal differences in score. 

While some findings, such as the positive impact of bedrooms on revenue, may seem intuitive, this analysis quantifies the effect and highlights where intuition aligns — or doesn’t — with the data.


  **Further Research**
- The R-squared value of 0.311 suggests that our model explains about 31.1% of the variance in yearly revenue. While this represents a moderate fit, it also indicates that a significant portion of revenue variation remains unexplained. Future analysis could explore additional variables such as location, availability, seasonality, or amenities to improve predictive power.

- I’d also like to compare this Airbnb data with real estate listings to assess whether the increase in yearly revenue justifies the potentially higher property costs associated with more bedrooms and bathrooms.


