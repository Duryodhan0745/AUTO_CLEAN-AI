import pandas as pd
import os

def load_csv(path: str) -> pd.DataFrame:
    """Load data from various file formats (CSV, Excel, JSON, Parquet, etc.)
    Handles special characters by converting or removing them.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    try:
        if ext == '.csv':
            # Try reading with different encodings and handle special chars
            try:
                df = pd.read_csv(path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(path, encoding='latin-1')
                except:
                    df = pd.read_csv(path, encoding='utf-8', errors='replace')
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(path)
        elif ext == '.json':
            df = pd.read_json(path)
        elif ext == '.parquet':
            df = pd.read_parquet(path)
        elif ext == '.tsv':
            try:
                df = pd.read_csv(path, sep='\t', encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(path, sep='\t', encoding='utf-8', errors='replace')
        else:
            # Try CSV as default with error handling
            try:
                df = pd.read_csv(path, encoding='utf-8')
            except:
                df = pd.read_csv(path, encoding='utf-8', errors='replace')
        
        if df.empty:
            raise ValueError("File contains no data.")
        
        # Clean column names - remove/replace special characters
        df.columns = [str(col).encode('ascii', 'ignore').decode('ascii').strip() 
                      if isinstance(col, str) else str(col) for col in df.columns]
        
        # Convert string columns: replace special characters with empty string
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: clean_text(x) if isinstance(x, str) else x)
        
        return df
    except Exception as e:
        raise ValueError(f"Failed to load file: {str(e)}")

def clean_text(text: str) -> str:
    """Remove or convert special characters in text"""
    import unicodedata
    # Try to normalize unicode characters
    try:
        text = unicodedata.normalize('NFKD', text)
        # Remove non-ASCII characters, keep only alphanumeric, spaces, and common punctuation
        text = text.encode('ascii', 'ignore').decode('ascii')
    except:
        pass
    return text
