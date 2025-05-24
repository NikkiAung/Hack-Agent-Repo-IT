import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from urllib.parse import urlparse

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Repository-Intelligence-Platform/1.0"
        }
        
        # Add GitHub token if available (for higher rate limits)
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    async def fetch_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch comprehensive repository data from GitHub API"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                # Fetch all data concurrently
                tasks = [
                    self._fetch_repo_info(session, owner, repo),
                    self._fetch_commits(session, owner, repo),
                    self._fetch_issues(session, owner, repo),
                    self._fetch_pull_requests(session, owner, repo),
                    self._fetch_contributors(session, owner, repo),
                    self._fetch_releases(session, owner, repo),
                    self._fetch_languages(session, owner, repo),
                    self._fetch_branches(session, owner, repo),
                    self._fetch_traffic(session, owner, repo),
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                return {
                    "repository": results[0] if not isinstance(results[0], Exception) else {},
                    "commits": results[1] if not isinstance(results[1], Exception) else [],
                    "issues": results[2] if not isinstance(results[2], Exception) else [],
                    "pull_requests": results[3] if not isinstance(results[3], Exception) else [],
                    "contributors": results[4] if not isinstance(results[4], Exception) else [],
                    "releases": results[5] if not isinstance(results[5], Exception) else [],
                    "languages": results[6] if not isinstance(results[6], Exception) else {},
                    "branches": results[7] if not isinstance(results[7], Exception) else [],
                    "traffic": results[8] if not isinstance(results[8], Exception) else {},
                }
            except Exception as e:
                print(f"Error fetching repository data: {e}")
                return {}
    
    async def _fetch_repo_info(self, session: aiohttp.ClientSession, owner: str, repo: str) -> Dict:
        """Fetch basic repository information"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def _fetch_commits(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict]:
        """Fetch recent commits (last 100)"""
        since = (datetime.now() - timedelta(days=30)).isoformat()
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"since": since, "per_page": 100}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def _fetch_issues(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict]:
        """Fetch issues and their metadata"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": "all", "per_page": 100}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def _fetch_pull_requests(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict]:
        """Fetch pull requests"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": "all", "per_page": 100}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def _fetch_contributors(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict]:
        """Fetch repository contributors"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {"per_page": 50}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def _fetch_releases(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict]:
        """Fetch repository releases"""
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        params = {"per_page": 20}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def _fetch_languages(self, session: aiohttp.ClientSession, owner: str, repo: str) -> Dict:
        """Fetch programming languages used"""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return {}
    
    async def _fetch_branches(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[Dict]:
        """Fetch repository branches"""
        url = f"{self.base_url}/repos/{owner}/{repo}/branches"
        params = {"per_page": 10}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
    
    async def _fetch_traffic(self, session: aiohttp.ClientSession, owner: str, repo: str) -> Dict:
        """Fetch traffic data (requires push access)"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/traffic/views"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except:
            pass
        return {}

    async def get_developer_insights(self, owner: str, repo: str, username: str = None) -> dict:
        """
        Compute all developer dashboard key insights and graph data.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch PRs (authored, reviewed, merged)
            prs_url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            prs_params = {"state": "all", "per_page": 100}
            async with session.get(prs_url, params=prs_params) as resp:
                all_prs = await resp.json() if resp.status == 200 else []

            # Fetch issues assigned to user
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            issues_params = {"state": "open", "assignee": username, "per_page": 100}
            async with session.get(issues_url, params=issues_params) as resp:
                assigned_issues = await resp.json() if resp.status == 200 else []

            # Fetch commits (last 30 days)
            since = (datetime.now() - timedelta(days=30)).isoformat()
            commits_url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            commits_params = {"since": since, "author": username, "per_page": 100}
            async with session.get(commits_url, params=commits_params) as resp:
                user_commits = await resp.json() if resp.status == 200 else []

            # PRs authored, reviewed, merged
            prs_authored = [pr for pr in all_prs if pr.get('user', {}).get('login') == username]
            prs_merged = [pr for pr in all_prs if pr.get('user', {}).get('login') == username and pr.get('merged_at')]
            # For reviewed PRs, need to fetch reviews for each PR
            prs_reviewed = []
            for pr in all_prs:
                reviews_url = pr.get('url', '') + '/reviews'
                async with session.get(reviews_url) as rresp:
                    reviews = await rresp.json() if rresp.status == 200 else []
                    if any(rv.get('user', {}).get('login') == username for rv in reviews):
                        prs_reviewed.append(pr)

            # Time to review/merge (for authored PRs)
            pr_cycle_times = []
            for pr in prs_authored:
                created = pr.get('created_at')
                merged = pr.get('merged_at')
                if created and merged:
                    t1 = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(merged.replace('Z', '+00:00'))
                    pr_cycle_times.append((t2 - t1).total_seconds() / 86400)
            avg_review_time = round(sum(pr_cycle_times) / len(pr_cycle_times), 2) if pr_cycle_times else 0

            # Pending review requests
            pending_reviews = [pr for pr in all_prs if pr.get('requested_reviewers') and any(u['login'] == username for u in pr['requested_reviewers'])]

            # Weekly contribution activity (commits, PRs)
            week_buckets = {}
            for c in user_commits:
                date = c['commit']['author']['date'][:10]
                week = datetime.fromisoformat(date).isocalendar()[1]
                week_buckets.setdefault(week, {"commits": 0, "prs": 0})
                week_buckets[week]["commits"] += 1
            for pr in prs_authored:
                date = pr['created_at'][:10]
                week = datetime.fromisoformat(date).isocalendar()[1]
                week_buckets.setdefault(week, {"commits": 0, "prs": 0})
                week_buckets[week]["prs"] += 1
            weekly_activity = [
                {"week": f"Week {w}", "commits": v["commits"], "prs": v["prs"]}
                for w, v in sorted(week_buckets.items())
            ]

            # PR state times (dummy for now)
            pr_state_times = {"awaiting_review": 0, "in_progress": 0}
            for pr in prs_authored:
                if pr.get('state') == 'open':
                    pr_state_times['in_progress'] += 1
                if pr.get('requested_reviewers'):
                    pr_state_times['awaiting_review'] += 1

            # Contribution heatmap (commits by day)
            heatmap = {}
            for c in user_commits:
                date = c['commit']['author']['date'][:10]
                heatmap[date] = heatmap.get(date, 0) + 1

            # PRs authored vs reviewed
            pr_distribution = [
                {"name": "Authored", "value": len(prs_authored)},
                {"name": "Reviewed", "value": len(prs_reviewed)}
            ]

            return {
                "key_insights": {
                    "prs_authored": len(prs_authored),
                    "prs_reviewed": len(prs_reviewed),
                    "prs_merged": len(prs_merged),
                    "avg_review_time_days": avg_review_time,
                    "pending_review_requests": len(pending_reviews),
                    "bugs_assigned": len(assigned_issues),
                    "weekly_contribution_activity": weekly_activity
                },
                "graphs_data": {
                    "pr_cycle_time": pr_cycle_times,
                    "weekly_commits_prs": weekly_activity,
                    "pr_distribution": pr_distribution,
                    "pr_state_times": pr_state_times,
                    "contribution_heatmap": heatmap
                }
            }

    async def get_em_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch PRs, contributors, files
            prs_url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            prs_params = {"state": "all", "per_page": 100}
            async with session.get(prs_url, params=prs_params) as resp:
                all_prs = await resp.json() if resp.status == 200 else []
            contributors_url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            async with session.get(contributors_url) as resp:
                contributors = await resp.json() if resp.status == 200 else []
            # Team-wide PR cycle times
            pr_cycle_times = []
            dev_prs = {}
            for pr in all_prs:
                author = pr.get('user', {}).get('login')
                dev_prs.setdefault(author, []).append(pr)
                created = pr.get('created_at')
                merged = pr.get('merged_at')
                if created and merged:
                    t1 = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(merged.replace('Z', '+00:00'))
                    pr_cycle_times.append((t2 - t1).total_seconds() / 86400)
            # Contribution load per developer
            contrib_load = {dev: len(prs) for dev, prs in dev_prs.items()}
            # Review distribution (dummy: count reviews per dev)
            review_dist = {dev: 0 for dev in contrib_load}
            for pr in all_prs:
                reviews_url = pr.get('url', '') + '/reviews'
                async with session.get(reviews_url) as rresp:
                    reviews = await rresp.json() if rresp.status == 200 else []
                    for rv in reviews:
                        reviewer = rv.get('user', {}).get('login')
                        if reviewer:
                            review_dist[reviewer] = review_dist.get(reviewer, 0) + 1
            # Bottlenecks: stale PRs (>5 days open)
            stale_prs = [pr for pr in all_prs if pr.get('state') == 'open' and (datetime.now() - datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))).days > 5]
            # Ownership risks: placeholder (would require code analysis)
            ownership_risks = []
            return {
                "key_insights": {
                    "team_pr_cycle_times": pr_cycle_times,
                    "contribution_load": contrib_load,
                    "review_distribution": review_dist,
                    "bottlenecks": len(stale_prs),
                    "ownership_risks": ownership_risks
                },
                "graphs_data": {
                    "team_heatmap": contrib_load,
                    "pr_review_time_box": pr_cycle_times,
                    "stale_prs_by_dev": {pr.get('user', {}).get('login'): 1 for pr in stale_prs},
                    "reviewer_author_network": review_dist,
                    "code_ownership_treemap": ownership_risks
                }
            }

    async def get_tpm_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch milestones, issues, PRs
            milestones_url = f"{self.base_url}/repos/{owner}/{repo}/milestones"
            async with session.get(milestones_url) as resp:
                milestones = await resp.json() if resp.status == 200 else []
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 100}) as resp:
                issues = await resp.json() if resp.status == 200 else []
            prs_url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            async with session.get(prs_url, params={"state": "all", "per_page": 100}) as resp:
                prs = await resp.json() if resp.status == 200 else []
            # Milestone progress (dummy: % closed issues)
            milestone_progress = []
            for m in milestones:
                total = m.get('open_issues', 0) + m.get('closed_issues', 0)
                pct = (m.get('closed_issues', 0) / total * 100) if total else 0
                milestone_progress.append({"title": m.get('title'), "progress": pct})
            # Blocking issues (label: 'blocked')
            blocking_issues = [i for i in issues if any(l['name'].lower() == 'blocked' for l in i.get('labels', []))]
            # Planned vs delivered (dummy: closed vs open issues)
            planned = len([i for i in issues if i['state'] == 'open'])
            delivered = len([i for i in issues if i['state'] == 'closed'])
            # Label trends
            label_trends = {}
            for i in issues:
                for l in i.get('labels', []):
                    label_trends[l['name']] = label_trends.get(l['name'], 0) + 1
            return {
                "key_insights": {
                    "milestone_progress": milestone_progress,
                    "blocking_issues": len(blocking_issues),
                    "planned_vs_delivered": {"planned": planned, "delivered": delivered},
                    "label_trends": label_trends
                },
                "graphs_data": {
                    "milestone_burndown": milestone_progress,
                    "gantt_chart": [],
                    "issue_types_by_milestone": label_trends,
                    "planned_vs_completed": {"planned": planned, "delivered": delivered},
                    "dependency_map": []
                }
            }

    async def get_pm_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch issues, PRs
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 100}) as resp:
                issues = await resp.json() if resp.status == 200 else []
            # Feature requests (label: 'feature')
            features = [i for i in issues if any(l['name'].lower() == 'feature' for l in i.get('labels', []))]
            bugs = [i for i in issues if any(l['name'].lower() == 'bug' for l in i.get('labels', []))]
            enhancements = [i for i in issues if any(l['name'].lower() == 'enhancement' for l in i.get('labels', []))]
            # User feedback (reactions/comments)
            feedback = sorted(issues, key=lambda i: (i.get('reactions', {}).get('+1', 0), i.get('comments', 0)), reverse=True)[:10]
            # Progress bars (dummy: % closed features)
            feature_progress = []
            for f in features:
                state = f['state']
                pct = 100 if state == 'closed' else 0
                feature_progress.append({"title": f.get('title'), "progress": pct})
            return {
                "key_insights": {
                    "feature_requests": len(features),
                    "bug_vs_feature": {"bugs": len(bugs), "features": len(features)},
                    "feature_progress": feature_progress,
                    "user_feedback": [{"title": i.get('title'), "reactions": i.get('reactions', {}), "comments": i.get('comments', 0)} for i in feedback]
                },
                "graphs_data": {
                    "issue_type_distribution": {"bugs": len(bugs), "features": len(features), "enhancements": len(enhancements)},
                    "issue_popularity": feedback,
                    "feature_completion": feature_progress,
                    "bug_inflow_outflow": [],
                    "feedback_tags": []
                }
            }

    async def get_qa_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch issues, PRs
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 100}) as resp:
                issues = await resp.json() if resp.status == 200 else []
            # Bugs by severity (label: 'bug', 'severity:high', etc.)
            bugs = [i for i in issues if any('bug' in l['name'].lower() for l in i.get('labels', []))]
            severity = {}
            for b in bugs:
                for l in b.get('labels', []):
                    if 'severity' in l['name'].lower():
                        severity[l['name']] = severity.get(l['name'], 0) + 1
            # Reopened issues (dummy: issues with 'reopened' label)
            reopened = [i for i in issues if any('reopened' in l['name'].lower() for l in i.get('labels', []))]
            # PRs missing tests (dummy: PRs with 'no-test' label)
            prs_missing_tests = [i for i in issues if any('no-test' in l['name'].lower() for l in i.get('labels', []))]
            # Bug resolution time (dummy: closed bugs)
            bug_resolution = []
            for b in bugs:
                if b['state'] == 'closed' and b.get('closed_at') and b.get('created_at'):
                    t1 = datetime.fromisoformat(b['created_at'].replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(b['closed_at'].replace('Z', '+00:00'))
                    bug_resolution.append((t2 - t1).total_seconds() / 86400)
            avg_bug_resolution = round(sum(bug_resolution) / len(bug_resolution), 2) if bug_resolution else 0
            return {
                "key_insights": {
                    "bugs_by_severity": severity,
                    "reopened_issues": len(reopened),
                    "prs_missing_tests": len(prs_missing_tests),
                    "avg_bug_resolution_days": avg_bug_resolution
                },
                "graphs_data": {
                    "bugs_by_severity": severity,
                    "bug_resolution_time": bug_resolution,
                    "recent_bugs": bugs[:10],
                    "bugs_reopened": len(reopened),
                    "module_stability": []
                }
            }

    async def get_scrum_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch issues, PRs
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 100}) as resp:
                issues = await resp.json() if resp.status == 200 else []
            # Sprint velocity (dummy: closed issues per sprint label)
            velocity = {}
            for i in issues:
                for l in i.get('labels', []):
                    if 'sprint' in l['name'].lower():
                        velocity[l['name']] = velocity.get(l['name'], 0) + (1 if i['state'] == 'closed' else 0)
            # Blocked issues (label: 'blocked')
            blocked = [i for i in issues if any('blocked' in l['name'].lower() for l in i.get('labels', []))]
            # Spillover (dummy: open issues with previous sprint label)
            spillover = [i for i in issues if i['state'] == 'open' and any('sprint' in l['name'].lower() for l in i.get('labels', []))]
            return {
                "key_insights": {
                    "sprint_velocity": velocity,
                    "sprint_spillover": len(spillover),
                    "blocked_issues": len(blocked)
                },
                "graphs_data": {
                    "burnup_burndown": velocity,
                    "completed_vs_planned": velocity,
                    "estimation_accuracy": [],
                    "blocked_issues_table": blocked,
                    "velocity_trend": []
                }
            }

    async def get_ux_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch issues, PRs
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 100}) as resp:
                issues = await resp.json() if resp.status == 200 else []
            # UX bugs (label: 'ux', 'ui')
            ux_bugs = [i for i in issues if any(l['name'].lower() in ['ux', 'ui'] for l in i.get('labels', []))]
            # Design PRs (label: 'design-review')
            design_prs = [i for i in issues if any('design-review' in l['name'].lower() for l in i.get('labels', []))]
            # Accessibility (label: 'a11y', 'accessibility')
            a11y = [i for i in issues if any(l['name'].lower() in ['a11y', 'accessibility'] for l in i.get('labels', []))]
            # Design progress (dummy: closed design PRs)
            design_progress = len([i for i in design_prs if i['state'] == 'closed']) / len(design_prs) * 100 if design_prs else 0
            return {
                "key_insights": {
                    "ux_bugs": len(ux_bugs),
                    "design_prs": len(design_prs),
                    "a11y_feedback": len(a11y),
                    "design_progress": design_progress
                },
                "graphs_data": {
                    "ux_issues_by_sprint": ux_bugs,
                    "design_progress": design_progress,
                    "design_prs_table": design_prs,
                    "a11y_issues": a11y,
                    "design_flow": []
                }
            }

    async def get_executive_insights(self, owner: str, repo: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch issues, PRs, contributors
            issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            async with session.get(issues_url, params={"state": "all", "per_page": 100}) as resp:
                issues = await resp.json() if resp.status == 200 else []
            prs_url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            async with session.get(prs_url, params={"state": "all", "per_page": 100}) as resp:
                prs = await resp.json() if resp.status == 200 else []
            contributors_url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            async with session.get(contributors_url) as resp:
                contributors = await resp.json() if resp.status == 200 else []
            # High-level delivery (dummy: closed PRs)
            delivery = len([pr for pr in prs if pr['state'] == 'closed'])
            # Efficiency trends (dummy: PRs per contributor)
            efficiency = {c['login']: c.get('contributions', 0) for c in contributors}
            # Bottlenecks (open issues)
            bottlenecks = len([i for i in issues if i['state'] == 'open'])
            # DORA metrics (dummy: PRs merged per week)
            dora = {"deployment_freq": len([pr for pr in prs if pr.get('merged_at')])}
            return {
                "key_insights": {
                    "delivery": delivery,
                    "efficiency": efficiency,
                    "bottlenecks": bottlenecks,
                    "dora_metrics": dora
                },
                "graphs_data": {
                    "delivery_progress": delivery,
                    "funnel": [],
                    "dora_dashboard": dora,
                    "blockers_by_team": bottlenecks,
                    "risk_vs_velocity": []
                }
            }

class GitHubAnalyzer:
    """Analyze GitHub data and extract meaningful metrics"""
    
    @staticmethod
    def analyze_commits(commits: List[Dict]) -> Dict[str, Any]:
        """Analyze commit patterns and activity"""
        if not commits:
            return {}
        
        # Group commits by date
        commit_dates = {}
        authors = {}
        total_additions = 0
        total_deletions = 0
        
        for commit in commits:
            date = commit['commit']['author']['date'][:10]  # YYYY-MM-DD
            author = commit['commit']['author']['name']
            
            commit_dates[date] = commit_dates.get(date, 0) + 1
            authors[author] = authors.get(author, 0) + 1
            
            # Note: additions/deletions require separate API calls for each commit
            # For now, we'll estimate based on commit frequency
        
        # Calculate metrics
        avg_commits_per_day = len(commits) / 30 if commits else 0
        active_days = len(commit_dates)
        top_contributors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_commits": len(commits),
            "avg_commits_per_day": round(avg_commits_per_day, 2),
            "active_days": active_days,
            "top_contributors": [{"name": name, "commits": count} for name, count in top_contributors],
            "commit_frequency": commit_dates,
            "unique_authors": len(authors)
        }
    
    @staticmethod
    def analyze_issues_and_prs(issues: List[Dict], prs: List[Dict]) -> Dict[str, Any]:
        """Analyze issues and pull requests"""
        # Separate issues from PRs (GitHub API returns both in issues endpoint)
        actual_issues = [item for item in issues if 'pull_request' not in item]
        
        # Analyze issues
        open_issues = [issue for issue in actual_issues if issue['state'] == 'open']
        closed_issues = [issue for issue in actual_issues if issue['state'] == 'closed']
        
        # Analyze PRs
        open_prs = [pr for pr in prs if pr['state'] == 'open']
        closed_prs = [pr for pr in prs if pr['state'] == 'closed']
        merged_prs = [pr for pr in closed_prs if pr.get('merged_at')]
        
        # Calculate average resolution time for closed issues
        avg_issue_resolution = GitHubAnalyzer._calculate_avg_resolution_time(closed_issues)
        avg_pr_merge_time = GitHubAnalyzer._calculate_avg_resolution_time(merged_prs)
        
        return {
            "issues": {
                "total": len(actual_issues),
                "open": len(open_issues),
                "closed": len(closed_issues),
                "avg_resolution_days": avg_issue_resolution
            },
            "pull_requests": {
                "total": len(prs),
                "open": len(open_prs),
                "closed": len(closed_prs),
                "merged": len(merged_prs),
                "avg_merge_days": avg_pr_merge_time
            }
        }
    
    @staticmethod
    def analyze_repository_health(repo_data: Dict) -> Dict[str, Any]:
        """Analyze overall repository health"""
        if not repo_data:
            return {}
        
        # Calculate health score based on various factors
        health_factors = {
            "has_description": bool(repo_data.get('description')),
            "has_readme": True,  # Assume true for now
            "has_license": bool(repo_data.get('license')),
            "has_issues_enabled": repo_data.get('has_issues', False),
            "has_wiki": repo_data.get('has_wiki', False),
            "recent_activity": (datetime.now().replace(tzinfo=None) - datetime.fromisoformat(
                repo_data.get('updated_at', '2020-01-01T00:00:00Z').replace('Z', '+00:00')
            ).replace(tzinfo=None)).days < 30,
            "has_topics": bool(repo_data.get('topics', [])),
        }
        
        health_score = sum(health_factors.values()) / len(health_factors) * 100
        
        return {
            "health_score": round(health_score, 1),
            "factors": health_factors,
            "stars": repo_data.get('stargazers_count', 0),
            "forks": repo_data.get('forks_count', 0),
            "watchers": repo_data.get('watchers_count', 0),
            "size_kb": repo_data.get('size', 0),
            "created_at": repo_data.get('created_at'),
            "updated_at": repo_data.get('updated_at'),
            "primary_language": repo_data.get('language'),
            "topics": repo_data.get('topics', [])
        }
    
    @staticmethod
    def _calculate_avg_resolution_time(items: List[Dict]) -> float:
        """Calculate average resolution time for issues/PRs"""
        if not items:
            return 0
        
        resolution_times = []
        for item in items:
            created = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
            closed = datetime.fromisoformat(item['closed_at'].replace('Z', '+00:00')).replace(tzinfo=None)
            resolution_times.append((closed - created).days)
        
        return round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else 0 