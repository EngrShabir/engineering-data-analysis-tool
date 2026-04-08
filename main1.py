from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

# Get script directory (VERY IMPORTANT)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class EngineeringData:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_csv(filepath)
        self.cols = [c for c in self.df.columns if c != "sample_id"]
        self.folder = os.path.dirname(os.path.abspath(filepath))

    def show_data(self):
        print("\n--- Raw Data ---")
        print(self.df.to_string(index=False))

    def analyze(self):
        print("\n--- Analysis ---")
        for col in self.cols:
            print(f"\n{col.upper()}")
            print(f"  Mean : {self.df[col].mean():.3f}")
            print(f"  Max  : {self.df[col].max():.3f}")
            print(f"  Min  : {self.df[col].min():.3f}")
            print(f"  Std  : {self.df[col].std():.3f}")

    def summary(self):
        print("\n--- Summary Highlights ---")
        for col in self.cols:
            max_id = self.df.loc[self.df[col].idxmax(), "sample_id"]
            min_id = self.df.loc[self.df[col].idxmin(), "sample_id"]
            print(f"  {col.upper()}: highest in sample {max_id}, lowest in sample {min_id}")

    def plot_column(self):
        print("\nAvailable columns:")
        for i, col in enumerate(self.cols, 1):
            print(f"  {i}. {col}")
        choice = input("Pick a column number to plot: ")
        try:
            col = self.cols[int(choice) - 1]
            self.df.plot(x="sample_id", y=col, marker="o", color="steelblue")
            plt.title(f"{col.upper()} vs Sample ID")
            plt.xlabel("Sample ID")
            plt.ylabel(col)
            plt.tight_layout()
            path = os.path.join(self.folder, f"{col}_chart.png")
            plt.savefig(path)
            print(f"Chart saved to {path}")
            plt.show()
        except (IndexError, ValueError):
            print("Invalid choice.")

    def plot_compare(self):
        print("\nAvailable columns:")
        for i, col in enumerate(self.cols, 1):
            print(f"  {i}. {col}")
        try:
            c1 = int(input("Pick first column number : ")) - 1
            c2 = int(input("Pick second column number: ")) - 1
            col1, col2 = self.cols[c1], self.cols[c2]
            self.df.plot(x="sample_id", y=[col1, col2], marker="o")
            plt.title(f"{col1.upper()} vs {col2.upper()}")
            plt.xlabel("Sample ID")
            plt.tight_layout()
            path = os.path.join(self.folder, f"{col1}_vs_{col2}_chart.png")
            plt.savefig(path)
            print(f"Chart saved to {path}")
            plt.show()
        except (IndexError, ValueError):
            print("Invalid choice.")

    def save_report(self):
        path = os.path.join(self.folder, "report.txt")
        with open(path, "w") as f:
            f.write("=== Engineering Data Analysis Report ===\n")
            f.write(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"File      : {self.filepath}\n\n")
            for col in self.cols:
                f.write(f"{col.upper()}\n")
                f.write(f"  Mean : {self.df[col].mean():.3f}\n")
                f.write(f"  Max  : {self.df[col].max():.3f}\n")
                f.write(f"  Min  : {self.df[col].min():.3f}\n")
                f.write(f"  Std  : {self.df[col].std():.3f}\n\n")
            f.write("--- Summary Highlights ---\n")
            for col in self.cols:
                max_id = self.df.loc[self.df[col].idxmax(), "sample_id"]
                min_id = self.df.loc[self.df[col].idxmin(), "sample_id"]
                f.write(f"  {col.upper()}: highest in sample {max_id}, lowest in sample {min_id}\n")
        print(f"\nReport saved to {path}")


def menu():
    while True:
        path = input("\nEnter CSV file path (press Enter for sample, or type 'exit'): ").strip()

        if path.lower() == "exit":
            print("Goodbye!")
            return

        # Default sample file (ALWAYS from script folder)
        if path == "":
            path = os.path.join(BASE_DIR, "data.csv")

        # If user gives relative name → convert to full path from script folder
        elif not os.path.isabs(path):
            path = os.path.join(BASE_DIR, path)

        if not os.path.exists(path):
            print("❌ File not found. Try again.")
            continue

        tool = EngineeringData(path)
        break

    while True:
        print("\n=== Engineering Data Tool ===")
        print("1. Show raw data")
        print("2. Analyze all columns")
        print("3. Summary highlights")
        print("4. Plot a single column")
        print("5. Compare two columns")
        print("6. Save report")
        print("7. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            tool.show_data()
        elif choice == "2":
            tool.analyze()
        elif choice == "3":
            tool.summary()
        elif choice == "4":
            tool.plot_column()
        elif choice == "5":
            tool.plot_compare()
        elif choice == "6":
            tool.save_report()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


menu()