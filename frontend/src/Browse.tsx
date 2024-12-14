import { Button, Spinner, TextInput, Toast } from "flowbite-react";
import { useState, useCallback, Suspense } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import { FaMagnifyingGlass } from "react-icons/fa6";
import PackageList from "./PackageList";

const fetchPackages = async (searchTerm: string) => {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/packages?q=${searchTerm}`,
  );
  return response.json();
};

type SearchInputs = {
  searchTerm: string;
};

export default function Browse() {
  const { register, handleSubmit } = useForm<SearchInputs>();
  const [searchTerm, setSearchTerm] = useState<string>("");

  const onSearch: SubmitHandler<SearchInputs> = useCallback(
    async (data: SearchInputs) => {
      setSearchTerm(data.searchTerm);
    },
    [],
  );

  return (
    <div className={"x-16"}>
      <div className="flex mt-8">
        <form onSubmit={handleSubmit(onSearch)} className="grow flex gap-2">
          <TextInput
            icon={FaMagnifyingGlass}
            placeholder="Enter a search term"
            className="grow"
            {...register("searchTerm")}
          />

          <Button type="submit">Search</Button>
        </form>
      </div>
      <div className="flex">
        {searchTerm === "" ? (
          <div>Try entering a search term.</div>
        ) : (
          <Suspense fallback={<Spinner size="xl" className="self-center" />}>
            <PackageList packagesPromise={fetchPackages(searchTerm)} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
