'use client';

import { useState } from 'react';
import LearningPath from '../components/LearningPath';

export default function Home() {
  return (
    <main className="bg-[#101a23] min-h-screen">
      <div className="container mx-auto pt-8 pb-16">
        <h1 className="text-3xl font-bold text-white text-center mb-8">
          GitHub Repository Onboarding Platform
        </h1>
        <LearningPath />
      </div>
    </main>
  );
}