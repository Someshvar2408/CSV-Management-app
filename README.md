
# CSV File Management Application  

A user-friendly web application for managing, analyzing, and visualizing CSV files. This application provides an intuitive interface for operations like uploading files, filtering data, adding rows, deleting files, and visualizing data trends.

---

## **Features**  
### 1. **File Upload**  
   - Upload CSV files to the server for processing.  
   - Displays confirmation upon successful upload.  

### 2. **Filter Data**  
   - Filter CSV data based on a specified value range.  
   - Download a new CSV file containing only the filtered rows.  

### 3. **Add Rows**  
   - Add multiple rows of data with a user-friendly interface.  
   - Select timestamps via a calendar picker and enter numeric values.  
   - Preview and edit rows before submitting them to the CSV file.  

### 4. **Delete Files**  
   - Delete unwanted CSV files directly from the application.  

### 5. **Data Visualization**  
   - Generate dynamic line charts to visualize data trends.  
   - View timestamps on the x-axis and corresponding values on the y-axis.  

---

## **Technologies Used**  
### **Frontend**  
- HTML5  
- CSS3  
- JavaScript  
- [Bootstrap](https://getbootstrap.com/) (for styling)  
- [Chart.js](https://www.chartjs.org/) (for data visualization)  

### **Backend**  
- Python  
- Flask  
- Flask-CORS (for handling cross-origin requests)  
- Pandas (for CSV file processing)  

---

## **Setup and Installation**  

### **Prerequisites**  
1. Python 3.8+  
2. Pip (Python package manager)  
3. Node.js (optional for frontend build systems)  

### **Steps to Run Locally**  
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/csv-management-app.git
   cd csv-management-app
   
2. Setup the backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
4. Install Dependencies
pip install -r requirements.txt

4.Run the Flask Server
python app.py

5.Access the application
  http://192.168.1.36:5000/ 

DIRECTORY STRUCTURE
csv-management-app/
├── app.py                  # Flask backend
├── templates/
│   └── index.html          # Frontend HTML
├── static/
│   ├── styles.css          # Custom CSS
│   └── scripts.js          # Frontend JavaScript
├── uploads/                # Directory for uploaded CSV files
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation



