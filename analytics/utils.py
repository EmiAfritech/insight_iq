import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import openai
from django.conf import settings
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Class for processing uploaded datasets
    """
    
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'json']
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process uploaded file and extract metadata
        """
        try:
            df = self.load_dataset(file_path)
            
            # Get basic information
            total_rows, total_columns = df.shape
            
            # Get column information
            columns_info = {}
            for col in df.columns:
                col_info = {
                    'name': col,
                    'type': str(df[col].dtype),
                    'null_count': int(df[col].isnull().sum()),
                    'unique_count': int(df[col].nunique()),
                    'sample_values': df[col].dropna().head(5).tolist()
                }
                
                # Add statistics for numeric columns
                if df[col].dtype in ['int64', 'float64']:
                    col_info.update({
                        'min': float(df[col].min()) if not df[col].isnull().all() else None,
                        'max': float(df[col].max()) if not df[col].isnull().all() else None,
                        'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                        'median': float(df[col].median()) if not df[col].isnull().all() else None,
                        'std': float(df[col].std()) if not df[col].isnull().all() else None,
                    })
                
                columns_info[col] = col_info
            
            return {
                'total_rows': total_rows,
                'total_columns': total_columns,
                'columns_info': columns_info,
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'has_duplicates': df.duplicated().any(),
                'duplicate_count': df.duplicated().sum(),
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise
    
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load dataset from file
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.csv':
                return pd.read_csv(file_path, encoding='utf-8')
            elif extension in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif extension == '.json':
                return pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {extension}")
        
        except UnicodeDecodeError:
            # Try different encodings
            if extension == '.csv':
                for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        return pd.read_csv(file_path, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
            raise ValueError("Unable to decode file with supported encodings")
        
        except Exception as e:
            logger.error(f"Error loading dataset {file_path}: {str(e)}")
            raise
    
    def clean_dataset(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Clean dataset based on configuration
        """
        cleaned_df = df.copy()
        
        # Remove duplicates
        if config.get('remove_duplicates', False):
            cleaned_df = cleaned_df.drop_duplicates()
        
        # Handle missing values
        missing_strategy = config.get('missing_strategy', 'keep')
        if missing_strategy == 'drop':
            cleaned_df = cleaned_df.dropna()
        elif missing_strategy == 'fill_mean':
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].mean())
        elif missing_strategy == 'fill_median':
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median())
        elif missing_strategy == 'fill_mode':
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else 'Unknown')
        
        # Remove outliers
        if config.get('remove_outliers', False):
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                Q1 = cleaned_df[col].quantile(0.25)
                Q3 = cleaned_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                cleaned_df = cleaned_df[(cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)]
        
        return cleaned_df


class AnalysisEngine:
    """
    Class for running different types of analysis
    """
    
    def __init__(self):
        self.processor = DataProcessor()
    
    def run_analysis(self, df: pd.DataFrame, analysis_type: str, config: Dict[str, Any], selected_columns: List[str]) -> Dict[str, Any]:
        """
        Run analysis based on type
        """
        try:
            # Filter columns if specified
            if selected_columns:
                df = df[selected_columns]
            
            # Clean data if needed
            if config.get('clean_data', True):
                df = self.processor.clean_dataset(df, config)
            
            # Run specific analysis
            if analysis_type == 'descriptive':
                return self._descriptive_analysis(df, config)
            elif analysis_type == 'correlation':
                return self._correlation_analysis(df, config)
            elif analysis_type == 'trend':
                return self._trend_analysis(df, config)
            elif analysis_type == 'predictive':
                return self._predictive_analysis(df, config)
            elif analysis_type == 'clustering':
                return self._clustering_analysis(df, config)
            elif analysis_type == 'anomaly':
                return self._anomaly_detection(df, config)
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        except Exception as e:
            logger.error(f"Error running {analysis_type} analysis: {str(e)}")
            raise
    
    def _descriptive_analysis(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform descriptive statistics analysis
        """
        results = {}
        
        # Basic statistics
        results['basic_stats'] = df.describe().to_dict()
        
        # Data types
        results['data_types'] = df.dtypes.to_dict()
        
        # Missing values
        results['missing_values'] = df.isnull().sum().to_dict()
        
        # Correlation matrix for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            results['correlation_matrix'] = df[numeric_cols].corr().to_dict()
        
        # Distribution statistics
        results['distributions'] = {}
        for col in numeric_cols:
            results['distributions'][col] = {
                'skewness': float(df[col].skew()),
                'kurtosis': float(df[col].kurtosis()),
                'quantiles': df[col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        results['categorical_analysis'] = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            results['categorical_analysis'][col] = {
                'unique_count': len(value_counts),
                'most_frequent': value_counts.index[0] if not value_counts.empty else None,
                'frequency_distribution': value_counts.head(10).to_dict()
            }
        
        return results
    
    def _correlation_analysis(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform correlation analysis
        """
        results = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Correlation analysis requires at least 2 numeric columns")
        
        # Pearson correlation
        corr_matrix = df[numeric_cols].corr()
        results['correlation_matrix'] = corr_matrix.to_dict()
        
        # Strong correlations (absolute value > 0.7)
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'column1': corr_matrix.columns[i],
                        'column2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        results['strong_correlations'] = strong_correlations
        
        # Covariance matrix
        results['covariance_matrix'] = df[numeric_cols].cov().to_dict()
        
        return results
    
    def _trend_analysis(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform trend analysis
        """
        results = {}
        
        # Identify date/time columns
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col])
                    date_cols.append(col)
                except:
                    continue
        
        if not date_cols:
            raise ValueError("Trend analysis requires at least one date/time column")
        
        date_col = date_cols[0]  # Use first date column
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Sort by date
        df = df.sort_values(date_col)
        
        # Numeric columns for trend analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        results['trends'] = {}
        for col in numeric_cols:
            # Calculate moving averages
            df[f'{col}_ma_7'] = df[col].rolling(window=7, min_periods=1).mean()
            df[f'{col}_ma_30'] = df[col].rolling(window=30, min_periods=1).mean()
            
            # Calculate trend direction
            first_half = df[col].iloc[:len(df)//2].mean()
            second_half = df[col].iloc[len(df)//2:].mean()
            trend_direction = 'increasing' if second_half > first_half else 'decreasing'
            
            results['trends'][col] = {
                'trend_direction': trend_direction,
                'change_percentage': float(((second_half - first_half) / first_half) * 100) if first_half != 0 else 0,
                'moving_average_7': df[f'{col}_ma_7'].tolist(),
                'moving_average_30': df[f'{col}_ma_30'].tolist(),
                'values': df[col].tolist(),
                'dates': df[date_col].dt.strftime('%Y-%m-%d').tolist()
            }
        
        return results
    
    def _predictive_analysis(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform predictive analysis using machine learning
        """
        results = {}
        
        target_column = config.get('target_column')
        if not target_column or target_column not in df.columns:
            raise ValueError("Predictive analysis requires a target column")
        
        # Prepare features
        feature_columns = [col for col in df.select_dtypes(include=[np.number]).columns if col != target_column]
        
        if len(feature_columns) == 0:
            raise ValueError("No numeric feature columns available for prediction")
        
        # Remove rows with missing values in target or features
        df_clean = df[feature_columns + [target_column]].dropna()
        
        if len(df_clean) < 10:
            raise ValueError("Not enough data for predictive analysis")
        
        X = df_clean[feature_columns]
        y = df_clean[target_column]
        
        # Split data (80% train, 20% test)
        split_index = int(len(df_clean) * 0.8)
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results['model_performance'] = {
            'mse': float(mse),
            'rmse': float(np.sqrt(mse)),
            'r2_score': float(r2),
            'feature_importance': dict(zip(feature_columns, model.coef_))
        }
        
        # Generate predictions for future values
        future_predictions = model.predict(X_test)
        results['predictions'] = {
            'actual': y_test.tolist(),
            'predicted': future_predictions.tolist(),
            'dates': df_clean.index[split_index:].tolist()
        }
        
        return results
    
    def _clustering_analysis(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform clustering analysis
        """
        results = {}
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Clustering analysis requires at least 2 numeric columns")
        
        # Prepare data
        df_numeric = df[numeric_cols].dropna()
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_numeric)
        
        # Determine optimal number of clusters
        n_clusters = config.get('n_clusters', 3)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to original data
        df_clustered = df_numeric.copy()
        df_clustered['cluster'] = cluster_labels
        
        # Cluster analysis
        results['cluster_centers'] = kmeans.cluster_centers_.tolist()
        results['cluster_labels'] = cluster_labels.tolist()
        results['n_clusters'] = n_clusters
        
        # Cluster statistics
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data = df_clustered[df_clustered['cluster'] == i][numeric_cols]
            cluster_stats[f'cluster_{i}'] = {
                'size': len(cluster_data),
                'mean': cluster_data.mean().to_dict(),
                'std': cluster_data.std().to_dict()
            }
        
        results['cluster_statistics'] = cluster_stats
        
        # PCA for visualization
        if len(numeric_cols) > 2:
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            results['pca_components'] = {
                'x': X_pca[:, 0].tolist(),
                'y': X_pca[:, 1].tolist(),
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist()
            }
        
        return results
    
    def _anomaly_detection(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform anomaly detection
        """
        results = {}
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            raise ValueError("Anomaly detection requires at least 1 numeric column")
        
        # Prepare data
        df_numeric = df[numeric_cols].dropna()
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_numeric)
        
        # Isolation Forest for anomaly detection
        contamination = config.get('contamination', 0.1)
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        
        # Anomaly scores
        anomaly_scores = iso_forest.decision_function(X_scaled)
        
        # Results
        results['anomaly_labels'] = anomaly_labels.tolist()
        results['anomaly_scores'] = anomaly_scores.tolist()
        results['n_anomalies'] = int(np.sum(anomaly_labels == -1))
        results['anomaly_percentage'] = float(np.sum(anomaly_labels == -1) / len(anomaly_labels) * 100)
        
        # Anomaly indices
        anomaly_indices = np.where(anomaly_labels == -1)[0]
        results['anomaly_indices'] = anomaly_indices.tolist()
        
        # Statistical outliers using IQR method
        statistical_outliers = {}
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
            statistical_outliers[col] = {
                'outlier_indices': outliers,
                'n_outliers': len(outliers),
                'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)}
            }
        
        results['statistical_outliers'] = statistical_outliers
        
        return results


class ChartGenerator:
    """
    Class for generating charts and visualizations
    """
    
    def __init__(self):
        pass
    
    def generate_charts(self, df: pd.DataFrame, analysis_type: str, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts based on analysis type and results
        """
        charts = []
        
        try:
            if analysis_type == 'descriptive':
                charts.extend(self._generate_descriptive_charts(df, results, selected_columns))
            elif analysis_type == 'correlation':
                charts.extend(self._generate_correlation_charts(df, results, selected_columns))
            elif analysis_type == 'trend':
                charts.extend(self._generate_trend_charts(df, results, selected_columns))
            elif analysis_type == 'predictive':
                charts.extend(self._generate_predictive_charts(df, results, selected_columns))
            elif analysis_type == 'clustering':
                charts.extend(self._generate_clustering_charts(df, results, selected_columns))
            elif analysis_type == 'anomaly':
                charts.extend(self._generate_anomaly_charts(df, results, selected_columns))
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")
            return []
    
    def _generate_descriptive_charts(self, df: pd.DataFrame, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts for descriptive analysis
        """
        charts = []
        
        # Histogram for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            fig = px.histogram(df, x=col, title=f'Distribution of {col}')
            charts.append({
                'name': f'{col} Distribution',
                'type': 'histogram',
                'data': json.loads(fig.to_json()),
                'config': {'displayModeBar': False}
            })
        
        # Bar chart for categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].nunique() <= 20:  # Only for columns with reasonable number of categories
                value_counts = df[col].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, title=f'Top 10 {col} Values')
                charts.append({
                    'name': f'{col} Top Values',
                    'type': 'bar',
                    'data': json.loads(fig.to_json()),
                    'config': {'displayModeBar': False}
                })
        
        return charts
    
    def _generate_correlation_charts(self, df: pd.DataFrame, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts for correlation analysis
        """
        charts = []
        
        # Correlation heatmap
        if 'correlation_matrix' in results:
            corr_matrix = pd.DataFrame(results['correlation_matrix'])
            fig = px.imshow(corr_matrix, title='Correlation Matrix', color_continuous_scale='RdYlBu')
            charts.append({
                'name': 'Correlation Heatmap',
                'type': 'heatmap',
                'data': json.loads(fig.to_json()),
                'config': {'displayModeBar': False}
            })
        
        # Scatter plots for strong correlations
        if 'strong_correlations' in results:
            for corr in results['strong_correlations'][:3]:  # Limit to top 3
                fig = px.scatter(df, x=corr['column1'], y=corr['column2'], 
                               title=f"{corr['column1']} vs {corr['column2']} (r={corr['correlation']:.3f})")
                charts.append({
                    'name': f"{corr['column1']} vs {corr['column2']}",
                    'type': 'scatter',
                    'data': json.loads(fig.to_json()),
                    'config': {'displayModeBar': False}
                })
        
        return charts
    
    def _generate_trend_charts(self, df: pd.DataFrame, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts for trend analysis
        """
        charts = []
        
        if 'trends' in results:
            for col, trend_data in results['trends'].items():
                # Time series plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_data['dates'],
                    y=trend_data['values'],
                    mode='lines',
                    name=col,
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=trend_data['dates'],
                    y=trend_data['moving_average_7'],
                    mode='lines',
                    name='7-day MA',
                    line=dict(color='red', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=trend_data['dates'],
                    y=trend_data['moving_average_30'],
                    mode='lines',
                    name='30-day MA',
                    line=dict(color='green', dash='dash')
                ))
                fig.update_layout(title=f'{col} Trend Analysis')
                
                charts.append({
                    'name': f'{col} Trend',
                    'type': 'line',
                    'data': json.loads(fig.to_json()),
                    'config': {'displayModeBar': False}
                })
        
        return charts
    
    def _generate_predictive_charts(self, df: pd.DataFrame, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts for predictive analysis
        """
        charts = []
        
        if 'predictions' in results:
            # Actual vs Predicted
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=results['predictions']['actual'],
                mode='lines+markers',
                name='Actual',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                y=results['predictions']['predicted'],
                mode='lines+markers',
                name='Predicted',
                line=dict(color='red')
            ))
            fig.update_layout(title='Actual vs Predicted Values')
            
            charts.append({
                'name': 'Actual vs Predicted',
                'type': 'line',
                'data': json.loads(fig.to_json()),
                'config': {'displayModeBar': False}
            })
        
        # Feature importance
        if 'model_performance' in results and 'feature_importance' in results['model_performance']:
            importance = results['model_performance']['feature_importance']
            fig = px.bar(x=list(importance.keys()), y=list(importance.values()), 
                        title='Feature Importance')
            charts.append({
                'name': 'Feature Importance',
                'type': 'bar',
                'data': json.loads(fig.to_json()),
                'config': {'displayModeBar': False}
            })
        
        return charts
    
    def _generate_clustering_charts(self, df: pd.DataFrame, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts for clustering analysis
        """
        charts = []
        
        # Cluster visualization
        if 'pca_components' in results:
            fig = px.scatter(
                x=results['pca_components']['x'],
                y=results['pca_components']['y'],
                color=results['cluster_labels'],
                title='Cluster Visualization (PCA)',
                labels={'x': 'PC1', 'y': 'PC2', 'color': 'Cluster'}
            )
            charts.append({
                'name': 'Cluster Visualization',
                'type': 'scatter',
                'data': json.loads(fig.to_json()),
                'config': {'displayModeBar': False}
            })
        
        # Cluster sizes
        cluster_sizes = [results['cluster_statistics'][f'cluster_{i}']['size'] 
                        for i in range(results['n_clusters'])]
        fig = px.pie(values=cluster_sizes, names=[f'Cluster {i}' for i in range(results['n_clusters'])],
                    title='Cluster Sizes')
        charts.append({
            'name': 'Cluster Sizes',
            'type': 'pie',
            'data': json.loads(fig.to_json()),
            'config': {'displayModeBar': False}
        })
        
        return charts
    
    def _generate_anomaly_charts(self, df: pd.DataFrame, results: Dict[str, Any], selected_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generate charts for anomaly detection
        """
        charts = []
        
        # Anomaly scatter plot
        if len(df.select_dtypes(include=[np.number]).columns) >= 2:
            numeric_cols = df.select_dtypes(include=[np.number]).columns[:2]
            colors = ['red' if label == -1 else 'blue' for label in results['anomaly_labels']]
            
            fig = px.scatter(
                df, x=numeric_cols[0], y=numeric_cols[1],
                color=colors,
                title='Anomaly Detection Results',
                labels={'color': 'Anomaly'}
            )
            charts.append({
                'name': 'Anomaly Detection',
                'type': 'scatter',
                'data': json.loads(fig.to_json()),
                'config': {'displayModeBar': False}
            })
        
        # Anomaly scores histogram
        fig = px.histogram(
            x=results['anomaly_scores'],
            title='Anomaly Scores Distribution',
            labels={'x': 'Anomaly Score', 'y': 'Count'}
        )
        charts.append({
            'name': 'Anomaly Scores',
            'type': 'histogram',
            'data': json.loads(fig.to_json()),
            'config': {'displayModeBar': False}
        })
        
        return charts


class InsightGenerator:
    """
    Class for generating AI-powered insights
    """
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    def generate_insights(self, df: pd.DataFrame, analysis_type: str, results: Dict[str, Any], charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate insights based on analysis results
        """
        insights = []
        
        try:
            if analysis_type == 'descriptive':
                insights.extend(self._generate_descriptive_insights(df, results))
            elif analysis_type == 'correlation':
                insights.extend(self._generate_correlation_insights(df, results))
            elif analysis_type == 'trend':
                insights.extend(self._generate_trend_insights(df, results))
            elif analysis_type == 'predictive':
                insights.extend(self._generate_predictive_insights(df, results))
            elif analysis_type == 'clustering':
                insights.extend(self._generate_clustering_insights(df, results))
            elif analysis_type == 'anomaly':
                insights.extend(self._generate_anomaly_insights(df, results))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    def _generate_descriptive_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for descriptive analysis
        """
        insights = []
        
        # Data quality insights
        missing_values = results.get('missing_values', {})
        high_missing = {col: count for col, count in missing_values.items() if count > len(df) * 0.1}
        
        if high_missing:
            insights.append({
                'title': 'High Missing Values Detected',
                'description': f"The following columns have more than 10% missing values: {', '.join(high_missing.keys())}. Consider data cleaning or imputation strategies.",
                'type': 'summary',
                'importance': 0.8,
                'confidence': 0.9
            })
        
        # Distribution insights
        if 'distributions' in results:
            for col, dist_info in results['distributions'].items():
                if abs(dist_info['skewness']) > 2:
                    skew_type = 'highly skewed' if abs(dist_info['skewness']) > 2 else 'moderately skewed'
                    direction = 'right' if dist_info['skewness'] > 0 else 'left'
                    insights.append({
                        'title': f'{col} Distribution Analysis',
                        'description': f"The {col} column is {skew_type} to the {direction} (skewness: {dist_info['skewness']:.2f}). This may indicate outliers or the need for data transformation.",
                        'type': 'anomaly',
                        'importance': 0.6,
                        'confidence': 0.8
                    })
        
        return insights
    
    def _generate_correlation_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for correlation analysis
        """
        insights = []
        
        # Strong correlations
        if 'strong_correlations' in results:
            for corr in results['strong_correlations']:
                correlation_strength = 'very strong' if abs(corr['correlation']) > 0.9 else 'strong'
                direction = 'positive' if corr['correlation'] > 0 else 'negative'
                
                insights.append({
                    'title': f"Strong Correlation: {corr['column1']} and {corr['column2']}",
                    'description': f"There is a {correlation_strength} {direction} correlation (r={corr['correlation']:.3f}) between {corr['column1']} and {corr['column2']}. This suggests these variables are closely related.",
                    'type': 'correlation',
                    'importance': 0.7,
                    'confidence': 0.9
                })
        
        return insights
    
    def _generate_trend_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for trend analysis
        """
        insights = []
        
        if 'trends' in results:
            for col, trend_data in results['trends'].items():
                change_pct = abs(trend_data['change_percentage'])
                direction = trend_data['trend_direction']
                
                if change_pct > 20:
                    significance = 'significant'
                elif change_pct > 10:
                    significance = 'moderate'
                else:
                    significance = 'minor'
                
                insights.append({
                    'title': f'{col} Trend Analysis',
                    'description': f"The {col} shows a {significance} {direction} trend with a {change_pct:.1f}% change over the analysis period.",
                    'type': 'trend',
                    'importance': 0.6 if change_pct > 10 else 0.4,
                    'confidence': 0.8
                })
        
        return insights
    
    def _generate_predictive_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for predictive analysis
        """
        insights = []
        
        if 'model_performance' in results:
            r2_score = results['model_performance']['r2_score']
            
            if r2_score > 0.8:
                model_quality = 'excellent'
            elif r2_score > 0.6:
                model_quality = 'good'
            elif r2_score > 0.4:
                model_quality = 'moderate'
            else:
                model_quality = 'poor'
            
            insights.append({
                'title': 'Model Performance Assessment',
                'description': f"The predictive model shows {model_quality} performance with an R² score of {r2_score:.3f}. This means {r2_score*100:.1f}% of the variance in the target variable is explained by the model.",
                'type': 'prediction',
                'importance': 0.8,
                'confidence': 0.9
            })
            
            # Feature importance insights
            if 'feature_importance' in results['model_performance']:
                importance = results['model_performance']['feature_importance']
                most_important = max(importance.items(), key=lambda x: abs(x[1]))
                
                insights.append({
                    'title': 'Key Predictive Factor',
                    'description': f"The most important feature for prediction is {most_important[0]} with an importance score of {most_important[1]:.3f}.",
                    'type': 'prediction',
                    'importance': 0.7,
                    'confidence': 0.8
                })
        
        return insights
    
    def _generate_clustering_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for clustering analysis
        """
        insights = []
        
        if 'cluster_statistics' in results:
            n_clusters = results['n_clusters']
            
            insights.append({
                'title': 'Data Segmentation Results',
                'description': f"The data has been successfully segmented into {n_clusters} distinct clusters, revealing natural groupings in your data.",
                'type': 'summary',
                'importance': 0.7,
                'confidence': 0.8
            })
            
            # Find largest and smallest clusters
            cluster_sizes = {k: v['size'] for k, v in results['cluster_statistics'].items()}
            largest_cluster = max(cluster_sizes.items(), key=lambda x: x[1])
            smallest_cluster = min(cluster_sizes.items(), key=lambda x: x[1])
            
            insights.append({
                'title': 'Cluster Size Distribution',
                'description': f"The largest cluster ({largest_cluster[0]}) contains {largest_cluster[1]} records, while the smallest ({smallest_cluster[0]}) contains {smallest_cluster[1]} records. This suggests varying densities in your data segments.",
                'type': 'summary',
                'importance': 0.6,
                'confidence': 0.8
            })
        
        return insights
    
    def _generate_anomaly_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights for anomaly detection
        """
        insights = []
        
        anomaly_percentage = results.get('anomaly_percentage', 0)
        n_anomalies = results.get('n_anomalies', 0)
        
        if anomaly_percentage > 10:
            severity = 'high'
        elif anomaly_percentage > 5:
            severity = 'moderate'
        else:
            severity = 'low'
        
        insights.append({
            'title': 'Anomaly Detection Results',
            'description': f"Detected {n_anomalies} anomalies ({anomaly_percentage:.1f}% of data), indicating a {severity} level of unusual patterns in your dataset.",
            'type': 'anomaly',
            'importance': 0.8 if anomaly_percentage > 5 else 0.6,
            'confidence': 0.8
        })
        
        # Statistical outliers
        if 'statistical_outliers' in results:
            for col, outlier_info in results['statistical_outliers'].items():
                if outlier_info['n_outliers'] > 0:
                    insights.append({
                        'title': f'{col} Outliers Detected',
                        'description': f"Found {outlier_info['n_outliers']} statistical outliers in {col}. Values outside the range {outlier_info['bounds']['lower']:.2f} to {outlier_info['bounds']['upper']:.2f} may need investigation.",
                        'type': 'anomaly',
                        'importance': 0.6,
                        'confidence': 0.9
                    })
        
        return insights
    
    def generate_ai_summary(self, analysis) -> str:
        """
        Generate AI-powered summary using OpenAI
        """
        if not settings.OPENAI_API_KEY:
            return "AI summary unavailable - OpenAI API key not configured."
        
        try:
            prompt = f"""
            Based on the following analysis results, provide a concise executive summary:
            
            Analysis Type: {analysis.analysis_type}
            Dataset: {analysis.dataset.name} ({analysis.dataset.total_rows} rows, {analysis.dataset.total_columns} columns)
            Results: {str(analysis.results)[:1000]}...
            
            Please provide a 2-3 sentence executive summary highlighting the key findings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return "Unable to generate AI summary at this time."
    
    def generate_ai_insights(self, analysis) -> List[Dict[str, Any]]:
        """
        Generate AI-powered insights
        """
        if not settings.OPENAI_API_KEY:
            return []
        
        try:
            prompt = f"""
            Based on the following analysis results, provide 3-5 key business insights:
            
            Analysis Type: {analysis.analysis_type}
            Dataset: {analysis.dataset.name}
            Results: {str(analysis.results)[:1000]}...
            
            Please provide actionable business insights in JSON format:
            [
                {{
                    "title": "Insight title",
                    "description": "Detailed description",
                    "importance": 0.8,
                    "confidence": 0.9
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content) if content.startswith('[') else []
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return []
    
    def generate_ai_recommendations(self, analysis) -> List[Dict[str, Any]]:
        """
        Generate AI-powered recommendations
        """
        if not settings.OPENAI_API_KEY:
            return []
        
        try:
            prompt = f"""
            Based on the following analysis results, provide 3-5 actionable recommendations:
            
            Analysis Type: {analysis.analysis_type}
            Dataset: {analysis.dataset.name}
            Results: {str(analysis.results)[:1000]}...
            
            Please provide actionable recommendations in JSON format:
            [
                {{
                    "title": "Recommendation title",
                    "description": "Detailed action plan",
                    "priority": "high|medium|low",
                    "effort": "high|medium|low"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content) if content.startswith('[') else []
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            return []
