import google.generativeai as genai
import os
import json
from typing import Dict, Any, List

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
        else:
            self.model = None
            print("Warning: GOOGLE_AI_API_KEY not found. Using fallback insights.")
    
    async def generate_role_insights(self, role: str, github_data: Dict[str, Any], 
                                   repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Generate role-specific insights using Gemini AI"""
        
        if not self.model:
            return self._get_fallback_insights(role, github_data, repo_owner, repo_name)
        
        try:
            # Prepare the data summary for AI analysis
            data_summary = self._prepare_data_summary(github_data)
            
            # Get role-specific prompt
            prompt = self._get_role_prompt(role, data_summary, repo_owner, repo_name)
            
            # Generate insights using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            insights = self._parse_gemini_response(response.text, role)
            
            return insights
            
        except Exception as e:
            print(f"Error generating Gemini insights: {e}")
            return self._get_fallback_insights(role, github_data, repo_owner, repo_name)
    
    def _prepare_data_summary(self, github_data: Dict[str, Any]) -> str:
        """Prepare a concise summary of GitHub data for AI analysis"""
        repo = github_data.get("repository", {})
        commits = github_data.get("commit_analysis", {})
        issues_prs = github_data.get("issues_prs_analysis", {})
        health = github_data.get("health_analysis", {})
        languages = github_data.get("languages", {})
        contributors = github_data.get("contributors", [])
        
        summary = f"""
        Repository Analysis Data:
        
        Basic Info:
        - Name: {repo.get('name', 'Unknown')}
        - Description: {repo.get('description', 'No description')}
        - Primary Language: {repo.get('language', 'Unknown')}
        - Stars: {repo.get('stargazers_count', 0)}
        - Forks: {repo.get('forks_count', 0)}
        - Created: {repo.get('created_at', 'Unknown')}
        - Last Updated: {repo.get('updated_at', 'Unknown')}
        
        Commit Activity (Last 30 days):
        - Total Commits: {commits.get('total_commits', 0)}
        - Average Commits/Day: {commits.get('avg_commits_per_day', 0)}
        - Active Days: {commits.get('active_days', 0)}
        - Unique Authors: {commits.get('unique_authors', 0)}
        
        Issues & Pull Requests:
        - Total Issues: {issues_prs.get('issues', {}).get('total', 0)}
        - Open Issues: {issues_prs.get('issues', {}).get('open', 0)}
        - Avg Issue Resolution: {issues_prs.get('issues', {}).get('avg_resolution_days', 0)} days
        - Total PRs: {issues_prs.get('pull_requests', {}).get('total', 0)}
        - Open PRs: {issues_prs.get('pull_requests', {}).get('open', 0)}
        - Merged PRs: {issues_prs.get('pull_requests', {}).get('merged', 0)}
        - Avg PR Merge Time: {issues_prs.get('pull_requests', {}).get('avg_merge_days', 0)} days
        
        Repository Health:
        - Health Score: {health.get('health_score', 0)}%
        - Has License: {health.get('factors', {}).get('has_license', False)}
        - Has Description: {health.get('factors', {}).get('has_description', False)}
        - Recent Activity: {health.get('factors', {}).get('recent_activity', False)}
        
        Languages: {', '.join(languages.keys()) if languages else 'None detected'}
        Contributors: {len(contributors)} total
        """
        
        return summary
    
    def _get_role_prompt(self, role: str, data_summary: str, repo_owner: str, repo_name: str) -> str:
        """Generate role-specific prompts for Gemini AI"""
        
        base_prompt = f"""
        Analyze the following GitHub repository data for {repo_owner}/{repo_name} and provide insights 
        specifically tailored for a {role}. 
        
        {data_summary}
        
        Please provide a JSON response with the following structure:
        {{
            "key_insights": ["insight1", "insight2", "insight3"],
            "metrics_summary": "A brief summary of the most important metrics for this role",
            "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
            "risk_assessment": "Assessment of potential risks or concerns",
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "summary": "A comprehensive 2-3 sentence summary for this role"
        }}
        """
        
        role_specific_prompts = {
            "developer": f"""
            {base_prompt}
            
            Focus on:
            - Code quality indicators
            - Development velocity and patterns
            - Technical debt signs
            - Collaboration patterns
            - Testing and documentation quality
            - Areas where code improvements are needed
            - Development workflow efficiency
            """,
            
            "em": f"""
            {base_prompt}
            
            Focus on:
            - Team productivity and velocity
            - Workload distribution among contributors
            - Process bottlenecks and inefficiencies
            - Team collaboration patterns
            - Resource allocation opportunities
            - Leadership and mentoring needs
            - Process improvement recommendations
            """,
            
            "pm": f"""
            {base_prompt}
            
            Focus on:
            - Feature delivery velocity
            - User feedback and issue patterns
            - Product roadmap alignment
            - Bug vs feature ratio
            - User engagement indicators
            - Product quality metrics
            - Feature prioritization insights
            """,
            
            "qa": f"""
            {base_prompt}
            
            Focus on:
            - Bug patterns and quality trends
            - Testing coverage indicators
            - Issue resolution patterns
            - Quality gate effectiveness
            - Regression patterns
            - Risk areas requiring testing attention
            - Quality improvement opportunities
            """,
            
            "executive": f"""
            {base_prompt}
            
            Focus on:
            - Strategic metrics and KPIs
            - ROI and business value indicators
            - Risk assessment and mitigation
            - Resource efficiency
            - Competitive positioning
            - Scalability and sustainability
            - Investment recommendations
            """
        }
        
        return role_specific_prompts.get(role, role_specific_prompts["developer"])
    
    def _parse_gemini_response(self, response_text: str, role: str) -> Dict[str, Any]:
        """Parse Gemini AI response into structured insights"""
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                insights = json.loads(json_str)
                return insights
            else:
                # Fallback parsing if JSON extraction fails
                return self._extract_insights_from_text(response_text, role)
                
        except json.JSONDecodeError:
            return self._extract_insights_from_text(response_text, role)
    
    def _extract_insights_from_text(self, text: str, role: str) -> Dict[str, Any]:
        """Extract insights from unstructured text response"""
        lines = text.split('\n')
        
        insights = {
            "key_insights": [],
            "metrics_summary": "",
            "recommendations": [],
            "risk_assessment": "",
            "strengths": [],
            "areas_for_improvement": [],
            "summary": ""
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to identify sections
            if "insight" in line.lower():
                current_section = "key_insights"
            elif "recommendation" in line.lower():
                current_section = "recommendations"
            elif "strength" in line.lower():
                current_section = "strengths"
            elif "improvement" in line.lower() or "concern" in line.lower():
                current_section = "areas_for_improvement"
            elif "summary" in line.lower():
                current_section = "summary"
            elif "risk" in line.lower():
                current_section = "risk_assessment"
            elif line.startswith('-') or line.startswith('*'):
                # This is a list item
                item = line[1:].strip()
                if current_section and current_section in insights:
                    if isinstance(insights[current_section], list):
                        insights[current_section].append(item)
                    else:
                        insights[current_section] = item
        
        # Ensure we have some content
        if not any(insights.values()):
            insights["summary"] = text[:200] + "..." if len(text) > 200 else text
        
        return insights
    
    def _get_fallback_insights(self, role: str, github_data: Dict[str, Any], 
                             repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Generate fallback insights when Gemini is not available"""
        
        repo = github_data.get("repository", {})
        commits = github_data.get("commit_analysis", {})
        issues_prs = github_data.get("issues_prs_analysis", {})
        health = github_data.get("health_analysis", {})
        
        fallback_insights = {
            "developer": {
                "key_insights": [
                    f"Repository has {commits.get('total_commits', 0)} commits in the last 30 days",
                    f"Average of {commits.get('avg_commits_per_day', 0)} commits per day",
                    f"Primary language is {repo.get('language', 'Unknown')}"
                ],
                "metrics_summary": f"Development activity shows {commits.get('total_commits', 0)} commits with {commits.get('unique_authors', 0)} contributors",
                "recommendations": [
                    "Review commit patterns for consistency",
                    "Ensure proper code review processes",
                    "Monitor technical debt accumulation"
                ],
                "risk_assessment": "Monitor for declining commit frequency or contributor dropout",
                "strengths": [
                    f"Active development with {commits.get('unique_authors', 0)} contributors",
                    f"Repository health score of {health.get('health_score', 0)}%"
                ],
                "areas_for_improvement": [
                    "Consider improving documentation",
                    "Review testing practices"
                ],
                "summary": f"Repository {repo_owner}/{repo_name} shows active development with room for process improvements."
            },
            
            "em": {
                "key_insights": [
                    f"Team has {commits.get('unique_authors', 0)} active contributors",
                    f"Average PR merge time is {issues_prs.get('pull_requests', {}).get('avg_merge_days', 0)} days",
                    f"Currently {issues_prs.get('pull_requests', {}).get('open', 0)} open pull requests"
                ],
                "metrics_summary": f"Team productivity shows {commits.get('avg_commits_per_day', 0)} commits/day with {issues_prs.get('pull_requests', {}).get('avg_merge_days', 0)} day average PR cycle",
                "recommendations": [
                    "Monitor workload distribution across team members",
                    "Optimize PR review process",
                    "Establish clear contribution guidelines"
                ],
                "risk_assessment": "Watch for PR bottlenecks and contributor burnout",
                "strengths": [
                    "Active contributor base",
                    "Regular commit activity"
                ],
                "areas_for_improvement": [
                    "Reduce PR cycle time",
                    "Balance workload distribution"
                ],
                "summary": f"Team shows good activity levels but could optimize collaboration processes for better efficiency."
            }
        }
        
        # Add similar structures for other roles...
        default_insight = fallback_insights.get("developer")
        
        return fallback_insights.get(role, default_insight)

    async def generate_onboarding_plan(self, prompt: str) -> dict:
        if not self.model:
            return {"steps": [], "tips": ["Gemini API key not set."], "summary": "No AI onboarding available."}
        try:
            response = self.model.generate_content(prompt)
            # Try to extract JSON from the response
            json_start = response.text.find('{')
            json_end = response.text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response.text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"steps": [], "tips": ["Could not parse onboarding plan."], "summary": response.text[:200]}
        except Exception as e:
            print(f"Error generating onboarding plan: {e}")
            return {"steps": [], "tips": [str(e)], "summary": "Failed to generate onboarding plan."}

    async def generate_code_tour(self, prompt: str) -> list:
        if not self.model:
            return [{"title": "No AI code tour available.", "description": "Gemini API key not set.", "file": "", "line": "", "snippet": "", "why": ""}]
        try:
            response = self.model.generate_content(prompt)
            json_start = response.text.find('[')
            json_end = response.text.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                json_str = response.text[json_start:json_end]
                return json.loads(json_str)
            else:
                return [{"title": "Could not parse code tour.", "description": response.text[:200], "file": "", "line": "", "snippet": "", "why": ""}]
        except Exception as e:
            print(f"Error generating code tour: {e}")
            return [{"title": "Failed to generate code tour.", "description": str(e), "file": "", "line": "", "snippet": "", "why": ""}]

    async def generate_issue_recommendations(self, prompt: str) -> list:
        if not self.model:
            return [{"title": "No AI recommendations.", "description": "Gemini API key not set.", "url": ""}]
        try:
            response = self.model.generate_content(prompt)
            json_start = response.text.find('[')
            json_end = response.text.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                json_str = response.text[json_start:json_end]
                return json.loads(json_str)
            else:
                return [{"title": "Could not parse recommendations.", "description": response.text[:200], "url": ""}]
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return [{"title": "Failed to generate recommendations.", "description": str(e), "url": ""}] 