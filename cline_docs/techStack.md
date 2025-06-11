# Technology Stack

## Programming Language
- Python 3.x
  - Chosen for its robust data processing capabilities
  - Extensive library support for CSV and Excel operations
  - Strong community support and documentation
  - Excellent string manipulation for data cleaning
  - Django web framework support

## Web Framework
- Django
  - Full-featured web framework
  - Built-in admin interface
  - Robust ORM for database operations
  - Comprehensive security features
  - URL routing and view handling
  - File upload handling
  - Template system

## Frontend Technologies
- HTML5
  - Semantic markup
  - File upload support
  - Drag and drop API
  - Form validation
- CSS3
  - Modern styling capabilities
  - Flexbox layout
  - Transitions and animations
  - Responsive design
- JavaScript
  - Async/await support
  - Fetch API
  - File handling
  - DOM manipulation
  - Form state management
  - Dynamic UI updates

## Core Libraries
### pandas
- Primary data manipulation library
- Efficient CSV file reading and writing
- DataFrame operations for data transformation
- Excel file generation capabilities
- Advanced data filtering and grouping
- Series operations for calculations
- Data type handling and conversion

### openpyxl
- Excel file handling
- Advanced formatting options
- Cell styling and column width adjustment
- Worksheet configuration
- Number format customization

## Data Processing Features
### Category Mapping
- Dictionary-based mapping system
- Flexible category definitions
- Easy to maintain and update

### Charge Calculations
- EU/RoW roaming differentiation
- Usage-based calculations
- Fixed charge processing
- Monetary value formatting

## File Formats
### Input
- CSV (Comma-Separated Values)
  - Service breakdown data
  - Usage data
  - Supports different data types
  - Handles missing values
  - Drag and drop upload support

### Output
- Excel (.xlsx)
  - Modern Excel format
  - Support for multiple sheets
  - Advanced formatting capabilities
  - Currency formatting
  - Column width optimization
  - Period information table

## Architecture Decisions
1. Web Application Architecture
   - Django backend for processing
   - HTML/CSS/JS frontend
   - Django URL patterns
   - Django view functions
   - File upload handling
   - Client-side validation
   - Asynchronous processing
   - State management
   - Dynamic UI components

2. Pandas DataFrame
   - Efficient data manipulation
   - Built-in data cleaning features
   - Excellent CSV and Excel support
   - Powerful grouping operations
   - Flexible data type handling

3. Modular Design
   - Separate functions for different operations
   - Easy to add new features
   - Maintainable codebase
   - Clear separation of concerns

4. Data Processing Strategy
   - Two-phase processing (service breakdown + usage)
   - Category-based charge mapping
   - Flexible calculation system
   - Robust data type handling
   - Temporary file management
   - Asynchronous processing
   - Form state persistence
   - Dynamic button visibility
   - User feedback system
