"use client";

import * as React from "react";
import { SearchBar } from "@/components/agptui/SearchBar";
import { FilterChips } from "@/components/agptui/FilterChips";
import { useRouter } from "next/navigation";

export const HeroSection: React.FC = () => {
  const router = useRouter();

  function onFilterChange(selectedFilters: string[]) {
    const encodedTerm = encodeURIComponent(selectedFilters.join(", "));
    router.push(`/store/search?searchTerm=${encodedTerm}`);
  }

  return (
    <div className="mb-2 mt-8 flex flex-col items-center justify-center px-4 sm:mb-4 sm:mt-12 sm:px-6 md:mb-6 md:mt-16 lg:my-24 lg:px-8 xl:my-16">
      <div className="w-full max-w-3xl lg:max-w-4xl xl:max-w-5xl">
        <div className="8md:mb-8 mb-4 text-center">
          <h1 className="text-center">
            <span className="font-h1 text-[#0a0a0a!important] dark:text-neutral-50">
              Explore AI agents built for{" "}
            </span>
            <span className="font-h1 text-[#7c3aed!important]">you</span>
            <br />
            <span className="font-h1 text-[#0a0a0a!important] dark:text-neutral-50">
              by the{" "}
            </span>
            <span className="font-h1 text-[#3b82f6!important]">community</span>
          </h1>
        </div>
        <h3 className="font-h3-geist mb-6 text-center dark:text-neutral-300 md:mb-12">
          Bringing you AI agents designed by thinkers from around the world
        </h3>
        <div className="mb-4 flex justify-center sm:mb-5 md:mb-6">
          <SearchBar height="h-[74px]" />
        </div>
        <div>
          <div className="flex justify-center">
            <FilterChips
              badges={[
                "Marketing",
                "SEO",
                "Content Creation",
                "Automation",
                "Fun",
              ]}
              onFilterChange={onFilterChange}
              multiSelect={false}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
