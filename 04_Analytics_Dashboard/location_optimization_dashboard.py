#!/usr/bin/env python3
"""
Real-time Location Optimization Dashboard
Web dashboard for monitoring TikTok USA audience optimization

Features:
- Real-time USA percentage monitoring
- Warm-up session tracking
- Alert management
- Performance analytics
- Automated action recommendations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
from sqlalchemy import create_engine, text, desc
from sqlalchemy.orm import sessionmaker

from location_optimization_system import LocationOptimizationSystem
from database.location_optimization_models import (
    LocationMetrics, WarmupSession, ProfileAnalysis, CommentManagement,
    PostingOptimization, SoundVerification, LocationOptimizationAlert,
    LocationOptimizationUtils
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiktok_location_optimization_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class LocationOptimizationDashboard:
    """
    Main dashboard class for location optimization monitoring
    """
    
    def __init__(self, database_url: str):
        self.db_engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.db_engine)
        self.location_system = LocationOptimizationSystem(database_url)
        
        # Dashboard configuration
        self.refresh_interval = 30  # seconds
        self.accounts = []  # Will be populated from database
        
    async def initialize_dashboard(self):
        """Initialize dashboard with account data"""
        session = self.Session()
        try:
            # Get all accounts from the database
            accounts_result = session.execute(text("""
                SELECT DISTINCT account FROM posts 
                WHERE created_at >= :date
                ORDER BY account
            """), {"date": datetime.utcnow() - timedelta(days=30)}).fetchall()
            
            self.accounts = [row.account for row in accounts_result]
            logger.info(f"📊 Dashboard initialized with {len(self.accounts)} accounts")
            
        finally:
            session.close()

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for all accounts
        
        Returns:
            Dictionary containing all dashboard data
        """
        dashboard_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'accounts': {},
            'system_status': 'operational',
            'alerts': [],
            'summary': {}
        }
        
        session = self.Session()
        try:
            # Get data for each account
            for account in self.accounts:
                account_data = await self._get_account_data(session, account)
                dashboard_data['accounts'][account] = account_data
            
            # Get system-wide alerts
            dashboard_data['alerts'] = await self._get_active_alerts(session)
            
            # Calculate summary statistics
            dashboard_data['summary'] = await self._calculate_summary_stats(dashboard_data['accounts'])
            
        finally:
            session.close()
        
        return dashboard_data

    async def _get_account_data(self, session, account: str) -> Dict[str, Any]:
        """Get comprehensive data for a specific account"""
        
        # Get latest location metrics
        latest_metrics = session.execute(text("""
            SELECT * FROM location_metrics 
            WHERE account = :account 
            ORDER BY recorded_at DESC 
            LIMIT 1
        """), {"account": account}).fetchone()
        
        # Get location metrics trend (last 7 days)
        metrics_trend = session.execute(text("""
            SELECT usa_percentage, recorded_at 
            FROM location_metrics 
            WHERE account = :account 
            AND recorded_at >= :date
            ORDER BY recorded_at ASC
        """), {
            "account": account,
            "date": datetime.utcnow() - timedelta(days=7)
        }).fetchall()
        
        # Get recent warm-up sessions
        recent_warmups = session.execute(text("""
            SELECT * FROM warmup_sessions 
            WHERE account = :account 
            ORDER BY started_at DESC 
            LIMIT 5
        """), {"account": account}).fetchall()
        
        # Get recent posting optimization data
        recent_posts = session.execute(text("""
            SELECT * FROM posting_optimization 
            WHERE account = :account 
            ORDER BY posted_at DESC 
            LIMIT 10
        """), {"account": account}).fetchall()
        
        # Get account alerts
        account_alerts = session.execute(text("""
            SELECT * FROM location_optimization_alerts 
            WHERE account = :account 
            AND is_resolved = FALSE
            ORDER BY triggered_at DESC
        """), {"account": account}).fetchall()
        
        return {
            'account': account,
            'current_metrics': {
                'usa_percentage': latest_metrics.usa_percentage if latest_metrics else 0,
                'total_audience': latest_metrics.total_audience if latest_metrics else 0,
                'confidence_score': latest_metrics.confidence_score if latest_metrics else 0,
                'last_updated': latest_metrics.recorded_at.isoformat() if latest_metrics else None
            } if latest_metrics else None,
            'metrics_trend': [
                {
                    'usa_percentage': row.usa_percentage,
                    'recorded_at': row.recorded_at.isoformat()
                } for row in metrics_trend
            ],
            'recent_warmups': [
                {
                    'session_id': row.session_id,
                    'session_type': row.session_type,
                    'duration_minutes': row.duration_minutes,
                    'success_score': row.success_score,
                    'started_at': row.started_at.isoformat(),
                    'completed_at': row.completed_at.isoformat() if row.completed_at else None,
                    'comments_made': row.comments_made,
                    'follows_made': row.follows_made
                } for row in recent_warmups
            ],
            'recent_posts': [
                {
                    'post_url': row.post_url,
                    'posted_at': row.posted_at.isoformat(),
                    'was_optimal_time': row.was_optimal_time,
                    'views_24h': row.views_24h,
                    'engagement_24h': row.engagement_24h,
                    'usa_percentage_24h': row.usa_percentage_24h
                } for row in recent_posts
            ],
            'alerts': [
                {
                    'alert_type': row.alert_type,
                    'alert_level': row.alert_level,
                    'message': row.message,
                    'triggered_at': row.triggered_at.isoformat(),
                    'recommendation': row.recommendation
                } for row in account_alerts
            ],
            'recommendations': await self._generate_account_recommendations(account, latest_metrics, recent_warmups)
        }

    async def _get_active_alerts(self, session) -> List[Dict[str, Any]]:
        """Get all active system alerts"""
        alerts_result = session.execute(text("""
            SELECT * FROM location_optimization_alerts 
            WHERE is_resolved = FALSE
            ORDER BY triggered_at DESC
        """)).fetchall()
        
        return [
            {
                'account': row.account,
                'alert_type': row.alert_type,
                'alert_level': row.alert_level,
                'message': row.message,
                'triggered_at': row.triggered_at.isoformat(),
                'recommendation': row.recommendation
            } for row in alerts_result
        ]

    async def _calculate_summary_stats(self, accounts_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for all accounts"""
        
        total_accounts = len(accounts_data)
        accounts_with_data = sum(1 for data in accounts_data.values() if data['current_metrics'])
        
        if accounts_with_data == 0:
            return {
                'total_accounts': total_accounts,
                'accounts_with_data': 0,
                'average_usa_percentage': 0,
                'critical_accounts': 0,
                'warning_accounts': 0,
                'optimal_accounts': 0,
                'total_alerts': 0
            }
        
        # Calculate averages
        usa_percentages = [
            data['current_metrics']['usa_percentage'] 
            for data in accounts_data.values() 
            if data['current_metrics']
        ]
        
        average_usa_percentage = sum(usa_percentages) / len(usa_percentages)
        
        # Count accounts by status
        critical_accounts = sum(1 for p in usa_percentages if p < 70)
        warning_accounts = sum(1 for p in usa_percentages if 70 <= p < 95)
        optimal_accounts = sum(1 for p in usa_percentages if p >= 95)
        
        # Count total alerts
        total_alerts = sum(
            len(data['alerts']) 
            for data in accounts_data.values()
        )
        
        return {
            'total_accounts': total_accounts,
            'accounts_with_data': accounts_with_data,
            'average_usa_percentage': round(average_usa_percentage, 2),
            'critical_accounts': critical_accounts,
            'warning_accounts': warning_accounts,
            'optimal_accounts': optimal_accounts,
            'total_alerts': total_alerts
        }

    async def _generate_account_recommendations(self, account: str, latest_metrics, recent_warmups) -> List[str]:
        """Generate recommendations for an account"""
        recommendations = []
        
        if not latest_metrics:
            recommendations.append("📊 No location metrics available - run initial analysis")
            return recommendations
        
        usa_percentage = latest_metrics.usa_percentage
        
        # USA percentage recommendations
        if usa_percentage < 70:
            recommendations.append("🚨 CRITICAL: USA % below 70% - Execute intensive warm-up immediately")
            recommendations.append("⏰ Schedule 30-minute warm-up sessions every 2 days")
            recommendations.append("🔍 Focus on USA-specific content and hashtags")
        elif usa_percentage < 95:
            recommendations.append("⚠️ WARNING: USA % below 95% - Execute maintenance warm-up")
            recommendations.append("⏰ Schedule 10-minute warm-up sessions daily")
            recommendations.append("💬 Engage only with confirmed USA users in comments")
        else:
            recommendations.append("✅ OPTIMAL: USA % above 95% - Continue current strategy")
            recommendations.append("⏰ Light 5-minute warm-up sessions every 3 days")
        
        # Warm-up recommendations
        if recent_warmups:
            last_warmup = recent_warmups[0]
            last_warmup_time = last_warmup['started_at']
            
            # Check if warm-up is needed
            time_since_warmup = datetime.utcnow() - datetime.fromisoformat(last_warmup_time)
            
            if usa_percentage < 95 and time_since_warmup > timedelta(hours=24):
                recommendations.append("🔥 Warm-up needed - Last session was over 24 hours ago")
            elif usa_percentage < 70 and time_since_warmup > timedelta(hours=48):
                recommendations.append("🚨 URGENT: Intensive warm-up needed - Last session was over 48 hours ago")
        
        # Posting time recommendations
        current_time = datetime.utcnow()
        optimal_windows = self.location_system.calculate_optimal_posting_time()
        
        in_optimal_window = any(
            start <= current_time.time() <= end 
            for start, end in optimal_windows
        )
        
        if not in_optimal_window:
            recommendations.append("⏰ Avoid posting now - Not in optimal time window")
            recommendations.append(f"📅 Optimal windows: {optimal_windows}")
        
        return recommendations

    def generate_metrics_chart(self, account_data: Dict[str, Any]) -> str:
        """Generate Plotly chart for metrics trend"""
        
        if not account_data['metrics_trend']:
            return json.dumps({})
        
        # Prepare data
        dates = [row['recorded_at'] for row in account_data['metrics_trend']]
        usa_percentages = [row['usa_percentage'] for row in account_data['metrics_trend']]
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=usa_percentages,
            mode='lines+markers',
            name='USA Percentage',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        # Add threshold lines
        fig.add_hline(y=95, line_dash="dash", line_color="green", 
                     annotation_text="95% - Optimal", annotation_position="top right")
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="70% - Critical", annotation_position="bottom right")
        
        # Update layout
        fig.update_layout(
            title=f"USA Percentage Trend - {account_data['account']}",
            xaxis_title="Date",
            yaxis_title="USA Percentage (%)",
            yaxis=dict(range=[0, 100]),
            showlegend=True,
            template="plotly_white"
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Flask routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('location_optimization_dashboard.html')

@app.route('/api/dashboard-data')
async def api_dashboard_data():
    """API endpoint for dashboard data"""
    dashboard = LocationOptimizationDashboard("sqlite:///tiktok_analytics.db")
    await dashboard.initialize_dashboard()
    data = await dashboard.get_dashboard_data()
    return jsonify(data)

@app.route('/api/account/<account_name>')
async def api_account_data(account_name):
    """API endpoint for specific account data"""
    dashboard = LocationOptimizationDashboard("sqlite:///tiktok_analytics.db")
    await dashboard.initialize_dashboard()
    
    session = dashboard.Session()
    try:
        account_data = await dashboard._get_account_data(session, account_name)
        return jsonify(account_data)
    finally:
        session.close()

@app.route('/api/chart/<account_name>')
async def api_account_chart(account_name):
    """API endpoint for account metrics chart"""
    dashboard = LocationOptimizationDashboard("sqlite:///tiktok_analytics.db")
    await dashboard.initialize_dashboard()
    
    session = dashboard.Session()
    try:
        account_data = await dashboard._get_account_data(session, account_name)
        chart_json = dashboard.generate_metrics_chart(account_data)
        return chart_json
    finally:
        session.close()

@app.route('/api/emergency-warmup/<account_name>')
async def api_emergency_warmup(account_name):
    """API endpoint for emergency warm-up execution"""
    try:
        # This would integrate with the warmup scheduler
        # For now, return a success response
        return jsonify({
            'status': 'success',
            'message': f'Emergency warm-up initiated for {account_name}',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to dashboard')
    emit('status', {'message': 'Connected to location optimization dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from dashboard')

@socketio.on('request_update')
async def handle_request_update():
    """Handle real-time update request"""
    try:
        dashboard = LocationOptimizationDashboard("sqlite:///tiktok_analytics.db")
        await dashboard.initialize_dashboard()
        data = await dashboard.get_dashboard_data()
        
        emit('dashboard_update', data)
    except Exception as e:
        emit('error', {'message': str(e)})

# Background task for real-time updates
def background_update_task():
    """Background task to send periodic updates"""
    while True:
        socketio.sleep(30)  # Update every 30 seconds
        
        try:
            # This would run the dashboard update logic
            socketio.emit('dashboard_update', {'timestamp': datetime.utcnow().isoformat()})
        except Exception as e:
            logger.error(f"Error in background update: {e}")

# Start background task
@socketio.on('connect')
def start_background_task():
    socketio.start_background_task(background_update_task)

if __name__ == '__main__':
    # Run the dashboard
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
