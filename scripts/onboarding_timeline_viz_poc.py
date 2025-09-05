import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns

def create_rollout_projection(total_repos, rates_per_week, start_date=None):
"""
Create a projection of repository feature rollout progress.

Args:
    total_repos (int): Total number of repositories
    rates_per_week (list): List of repos per week rates to compare
    start_date (datetime): Start date for the rollout (default: today)

Returns:
    DataFrame with projections for each rate
"""

if start_date is None:
    start_date = datetime.now()

# Create results dictionary
results = {}

for rate in rates_per_week:
    weeks_needed = np.ceil(total_repos / rate)
    weeks = np.arange(0, weeks_needed + 1)
    
    # Calculate cumulative repos enabled
    repos_enabled = np.minimum(weeks * rate, total_repos)
    
    # Create dates
    dates = [start_date + timedelta(weeks=w) for w in weeks]
    
    results[f'{rate} per week'] = {
        'dates': dates,
        'repos_enabled': repos_enabled,
        'completion_date': dates[-1],
        'weeks_to_complete': weeks_needed
    }

return results

def plot_rollout_comparison(total_repos=2500, rates=[5, 10, 15, 20],
start_date=None, figsize=(12, 8)):
"""
Create visualization comparing different rollout rates.
"""

# Generate projections
projections = create_rollout_projection(total_repos, rates, start_date)


# Set up the plot
plt.figure(figsize=figsize)

# Color palette
colors = plt.cm.Set1(np.linspace(0, 1, len(rates)))

# Plot each rate scenario
for i, (label, data) in enumerate(projections.items()):
    plt.plot(data['dates'], data['repos_enabled'], 
            label=label, linewidth=2.5, color=colors[i])
    
    # Add completion point marker
    plt.scatter(data['completion_date'], total_repos, 
               color=colors[i], s=80, zorder=5)

# Formatting
plt.axhline(y=total_repos, color='red', linestyle='--', alpha=0.7, 
            label=f'Target: {total_repos} repos')

plt.xlabel('Date', fontsize=12)
plt.ylabel('Repositories Enabled', fontsize=12)
plt.title(f'Feature Rollout Progress Projection\n({total_repos:,} Total Repositories)', 
          fontsize=14, fontweight='bold')

plt.grid(True, alpha=0.3)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Format y-axis to show thousands
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

return projections


def create_summary_table(projections, total_repos):
"""
Create a summary table of completion timelines.
"""
summary_data = []


for label, data in projections.items():
    rate = int(label.split()[0])
    completion_date = data['completion_date']
    weeks_to_complete = data['weeks_to_complete']
    months_to_complete = weeks_to_complete / 4.33  # Average weeks per month
    
    summary_data.append({
        'Rate (repos/week)': rate,
        'Weeks to Complete': f'{weeks_to_complete:.0f}',
        'Months to Complete': f'{months_to_complete:.1f}',
        'Completion Date': completion_date.strftime('%Y-%m-%d'),
        'Repos per Day': f'{rate/7:.1f}'
    })

return pd.DataFrame(summary_data)


def plot_weekly_workload(rates=[5, 10, 15, 20], figsize=(10, 6)):
"""
Create a bar chart showing weekly workload for different rates.
"""
plt.figure(figsize=figsize)


# Create data
weeks_data = []
repos_per_day_data = []

for rate in rates:
    weeks_data.append(2500 / rate)
    repos_per_day_data.append(rate / 7)

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

# Plot 1: Weeks to completion
bars1 = ax1.bar(range(len(rates)), weeks_data, color='steelblue', alpha=0.7)
ax1.set_xlabel('Rate (repos/week)')
ax1.set_ylabel('Weeks to Complete')
ax1.set_title('Time to Complete Rollout')
ax1.set_xticks(range(len(rates)))
ax1.set_xticklabels([f'{r}/week' for r in rates])

# Add value labels on bars
for bar, weeks in zip(bars1, weeks_data):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{weeks:.0f}w\n({weeks/4.33:.1f}m)', 
            ha='center', va='bottom', fontsize=9)

# Plot 2: Daily workload
bars2 = ax2.bar(range(len(rates)), repos_per_day_data, color='orange', alpha=0.7)
ax2.set_xlabel('Rate (repos/week)')
ax2.set_ylabel('Repos per Day')
ax2.set_title('Daily Workload')
ax2.set_xticks(range(len(rates)))
ax2.set_xticklabels([f'{r}/week' for r in rates])

# Add value labels on bars
for bar, daily in zip(bars2, repos_per_day_data):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{daily:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
return fig


# Example usage and demonstration

if **name** == “**main**”:
# Set style
plt.style.use(‘default’)
sns.set_palette(“husl”)


# Example 1: Main projection chart
print("Creating rollout projection visualization...")
projections = plot_rollout_comparison(
    total_repos=2500, 
    rates=[5, 8, 10, 15, 20],
    start_date=datetime(2024, 1, 1)
)
plt.show()

# Example 2: Summary table
print("\nRollout Summary:")
summary = create_summary_table(projections, 2500)
print(summary.to_string(index=False))

# Example 3: Workload comparison
print("\nCreating workload comparison...")
plot_weekly_workload([5, 8, 10, 15, 20])
plt.show()

# Example 4: Interactive scenario planning
def quick_scenario(rate, total=2500):
    weeks = np.ceil(total / rate)
    months = weeks / 4.33
    daily = rate / 7
    print(f"\nScenario: {rate} repos/week")
    print(f"  Time to complete: {weeks:.0f} weeks ({months:.1f} months)")
    print(f"  Daily workload: {daily:.1f} repos/day")
    print(f"  Completion date: {(datetime.now() + timedelta(weeks=weeks)).strftime('%Y-%m-%d')}")

print("\n" + "="*50)
print("QUICK SCENARIO ANALYSIS")
print("="*50)
for rate in [5, 10, 15]:
    quick_scenario(rate)
