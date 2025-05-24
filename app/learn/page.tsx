import React from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const Learn = () => {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <main>
          <section className="mb-10">
            <h2 className="text-4xl font-semibold tracking-tight mb-4">
              My Learning Path
            </h2>
            <div className="bg-[#1a1e22] p-6 rounded-xl shadow-lg mb-8">
              <div className="flex justify-between items-center mb-2">
                <p className="text-white text-base font-medium">
                  Overall Progress
                </p>
                <p className="text-[#3d98f4] text-sm font-semibold">60%</p>
              </div>
              <div className="w-full bg-[#314d68] rounded-full h-2.5">
                <div
                  className="bg-[#3d98f4] h-2.5 rounded-full"
                  style={{ width: "60%" }}
                ></div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold tracking-tight mb-6">
              Learning Chapters
            </h2>

            <Accordion type="single" collapsible className="space-y-4">
              <AccordionItem
                value="chapter-1"
                className="bg-[#1a1e22] rounded-xl border-none"
              >
                <AccordionTrigger className="px-6 py-4 hover:no-underline">
                  <div className="flex items-center gap-4 w-full">
                    <div className="text-white flex items-center justify-center rounded-lg bg-[#223649] shrink-0 size-12">
                      <svg
                        fill="currentColor"
                        height="24px"
                        viewBox="0 0 256 256"
                        width="24px"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M224,48H160a40,40,0,0,0-32,16A40,40,0,0,0,96,48H32A16,16,0,0,0,16,64V192a16,16,0,0,0,16,16H96a24,24,0,0,1,24,24,8,8,0,0,0,16,0,24,24,0,0,1,24-24h64a16,16,0,0,0,16-16V64A16,16,0,0,0,224,48ZM96,192H32V64H96a24,24,0,0,1,24,24V200A39.81,39.81,0,0,0,96,192Zm128,0H160a39.81,39.81,0,0,0-24,8V88a24,24,0,0,1,24-24h64Z"></path>
                      </svg>
                    </div>
                    <div className="flex-grow text-left">
                      <p className="text-white text-lg font-semibold leading-tight">
                        Chapter 1: Introduction
                      </p>
                      <p className="text-[#90adcb] text-sm font-normal mt-1">
                        Introduction to the codebase and its core
                        functionalities.
                      </p>
                    </div>
                    <div className="shrink-0 flex items-center gap-3">
                      <div className="w-20 bg-[#314d68] rounded-full h-2">
                        <div
                          className="bg-[#3d98f4] h-2 rounded-full"
                          style={{ width: "80%" }}
                        ></div>
                      </div>
                      <p className="text-white text-sm font-medium w-8 text-right">
                        80%
                      </p>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-4">
                  <div className="space-y-4">
                    <p className="text-[#90adcb] text-sm">
                      This chapter covers the fundamental concepts of our
                      codebase including:
                    </p>
                    <ul className="list-disc list-inside space-y-2 text-[#90adcb] text-sm ml-4">
                      <li>Project structure and organization</li>
                      <li>Core technologies and frameworks used</li>
                      <li>Development environment setup</li>
                      <li>Basic coding conventions and standards</li>
                    </ul>
                    <div className="flex gap-2 mt-4">
                      <button className="px-4 py-2 bg-[#3d98f4] text-white rounded-lg text-sm font-medium hover:bg-[#2d7ce0] transition-colors">
                        Continue Learning
                      </button>
                      <button className="px-4 py-2 bg-[#223649] text-white rounded-lg text-sm font-medium hover:bg-[#2a3f56] transition-colors">
                        Review Notes
                      </button>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </section>
        </main>
      </div>
    </div>
  );
};

export default Learn;
