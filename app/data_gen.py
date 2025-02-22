import pandas as pd
import random
from datetime import datetime, timedelta

def generate_marketing_data_for_ads(data_list, start_date="2024-06-01", end_date="2024-06-30", output_file="marketing_data.csv"):
    # Define channels and metrics
    channels = ['Facebook', 'Instagram', 'Google Ads', 'Email Campaign', 'Twitter']
    
    # Convert dates to datetime format
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Generate data
    data_rows = []
    for ad_data in data_list:
        product_service = ad_data.get('Product/Service Overview', 'Unknown Product/Service')
        target_audience = ad_data.get('Target Audience', 'General Audience')
        campaign_goal = ad_data.get('Campaign Goal', 'Brand Awareness')

        date = start_date
        while date <= end_date:
            for channel in channels:
                impressions = random.randint(500, 5000)
                clicks = random.randint(50, impressions // 10)
                conversions = random.randint(1, clicks // 5) if clicks > 0 else 0
                ctr = (clicks / impressions) * 100 if impressions > 0 else 0
                cost = round(random.uniform(20, 200), 2)

                data_rows.append([
                    date.strftime('%Y-%m-%d'), product_service, target_audience, campaign_goal, channel, 
                    impressions, clicks, conversions, round(ctr, 2), cost
                ])

            date += timedelta(days=1)

    # Create DataFrame
    df = pd.DataFrame(data_rows, columns=[
        'Date', 'Product/Service', 'Target Audience', 'Campaign Goal', 'Channel', 
        'Impressions', 'Clicks', 'Conversions', 'CTR (%)', 'Cost ($)'
    ])
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Marketing data successfully written to {output_file}")
    
    return df

# Example usage
example_ads = [
    {
        'Product/Service Overview': 'Pick Your Own Strawberries This Summer!',
        'Target Audience': 'Families, Kids, Nature Enthusiasts',
        'Campaign Goal': 'Create unforgettable memories at the farm'
    },
    {
        'Product/Service Overview': 'Get Ready for Strawberry Season!',
        'Target Audience': 'Home Cooks, Fruit Lovers',
        'Campaign Goal': 'Encourage fresh strawberry purchases'
    },
    {
        'Product/Service Overview': 'Strawberry Picking Fun for All Ages!',
        'Target Audience': 'Multi-generational Families',
        'Campaign Goal': 'Make strawberry picking a family tradition'
    }
]

# Generate and save data
marketing_df = generate_marketing_data_for_ads(example_ads)
