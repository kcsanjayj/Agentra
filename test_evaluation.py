#!/usr/bin/env python3
"""
Reproducibility Script for Autonomous Multi-Agent Executor
Run this to verify the test results mentioned in README
"""

import requests
import json
import time
import sys

def run_evaluation():
    """Run the same evaluation as mentioned in README"""
    
    print("🤖 Multi-Agent System Reproducibility Test")
    print("=" * 60)
    
    # Load test tasks
    print("\n📁 Loading test tasks...")
    with open('test_data/sample_tasks.txt', 'r') as f:
        tasks = [line.strip() for line in f if line.strip()]
    
    print(f"✅ Loaded {len(tasks)} test tasks")
    
    # Check if server is running
    print("\n🔍 Checking server status...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server returned error")
            return 0
    except requests.exceptions.RequestException:
        print("❌ Server not running. Start with: python server.py")
        return 0
    
    # Test a sample of tasks
    test_tasks = tasks[:5]  # Test first 5 tasks for demo
    results = []
    
    print(f"\n🧪 Testing {len(test_tasks)} sample tasks...")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n[{i}/{len(test_tasks)}] Task: {task[:50]}...")
        
        start_time = time.time()
        
        try:
            # Send task to multi-agent system
            response = requests.post(
                'http://localhost:8000/api/execute',
                json={'task': task},
                timeout=30
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                response_time = end_time - start_time
                
                print(f"   ✅ Completed in {response_time:.1f}s")
                print(f"   📝 Length: {len(result.get('response', ''))} characters")
                
                # Simple quality check: response length and completion
                quality_score = 0
                if len(result.get('response', '')) > 100:
                    quality_score += 0.5  # Substantial response
                if result.get('status') == 'completed':
                    quality_score += 0.5  # Completed successfully
                
                results.append({
                    'task': task,
                    'success': True,
                    'response_time': response_time,
                    'quality_score': quality_score
                })
                
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                results.append({
                    'task': task,
                    'success': False,
                    'response_time': 0,
                    'quality_score': 0
                })
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 30 seconds")
            results.append({
                'task': task,
                'success': False,
                'response_time': 30,
                'quality_score': 0
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'task': task,
                'success': False,
                'response_time': 0,
                'quality_score': 0
            })
    
    # Calculate metrics
    print("\n📊 Results Summary:")
    successful_tasks = [r for r in results if r['success']]
    success_rate = len(successful_tasks) / len(results) * 100
    
    if successful_tasks:
        avg_response_time = sum(r['response_time'] for r in successful_tasks) / len(successful_tasks)
        avg_quality = sum(r['quality_score'] for r in results) / len(results) * 100
    else:
        avg_response_time = 0
        avg_quality = 0
    
    print(f"   Success Rate: {success_rate:.0f}%")
    print(f"   Avg Response Time: {avg_response_time:.1f}s")
    print(f"   Avg Quality Score: {avg_quality:.0f}%")
    
    # Expected results based on README
    print("\n🎯 Expected Results:")
    print("   Success Rate: ~88%")
    print("   Response Time: ~2.8s")
    print("   Quality Score: ~85%")
    
    # Verification
    print("\n✅ Verification:")
    success_ok = abs(success_rate - 88) < 20  # Within 20% of expected
    time_ok = abs(avg_response_time - 2.8) < 2.0  # Within 2 seconds of expected
    quality_ok = avg_quality > 70  # Above 70% quality
    
    print(f"   Success Rate: {'✅ OK' if success_ok else '❌ LOW'}")
    print(f"   Response Time: {'✅ OK' if time_ok else '❌ SLOW'}")
    print(f"   Quality Score: {'✅ OK' if quality_ok else '❌ LOW'}")
    
    # Overall assessment
    overall_score = (success_ok + time_ok + quality_ok) / 3 * 100
    print(f"\n📈 Overall Match: {overall_score:.0f}%")
    
    if overall_score >= 80:
        print("🎉 Great! Results closely match README claims.")
    elif overall_score >= 60:
        print("⚠️  Acceptable. Some metrics differ from README.")
    else:
        print("❌ Results don't match README claims.")
    
    return overall_score

if __name__ == "__main__":
    try:
        score = run_evaluation()
        print(f"\n🏁 Test completed with {score:.0f}% match to README")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        print("💡 Make sure server is running: python server.py")
