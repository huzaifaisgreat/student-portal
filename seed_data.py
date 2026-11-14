"""seed_data.py - fill the portal with sample students (run once: python seed_data.py)."""
import backend

SAMPLE = [
    ("25L-5308", "Ayesha Khan", "Computer Science", 3, 88),
    ("25L-5291", "Bilal Ahmed", "Computer Science", 3, 72.5),
    ("25L-5101", "Sara Malik", "Software Engineering", 2, 91),
    ("25L-5112", "Hamza Tariq", "Software Engineering", 2, 64),
    ("25L-5127", "Maryam Iqbal", "Electrical Engineering", 4, 79),
    ("25L-5133", "Usman Raza", "Electrical Engineering", 4, 48),
    ("25L-5148", "Zainab Fatima", "Business Administration", 1, 83),
    ("25L-5160", "Ali Hassan", "Business Administration", 1, 36),
    ("25L-5172", "Hira Noor", "Law", 5, 95),
    ("25L-5185", "Fahad Siddiqui", "Law", 5, 58),
    ("25L-5190", "Noor Ul Ain", "Computer Science", 6, 76),
    ("25L-5204", "Daniyal Shah", "Software Engineering", 6, 69),
]

if __name__ == "__main__":
    backend.load_users()
    for roll, name, dept, sem, marks in SAMPLE:
        ok, msg = backend.add_record({"roll_no": roll, "name": name, "department": dept,
                                      "semester": sem, "marks": marks})
        print(msg[0])
