import { Button, Spinner, TextInput, Toast } from "flowbite-react";
import { useCallback, useState } from "preact/hooks";
import { SubmitHandler, useForm } from "react-hook-form";
import { FaMagnifyingGlass } from "react-icons/fa6";

type SearchInputs = {
  searchTerm: string;
};

type Package = {
  id: number;
  name: string;
  downloads_total: number;
};

export default function Browse() {
  const { register, handleSubmit } = useForm<SearchInputs>();
  const [packages, setPackages] = useState<Package[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const onSearch: SubmitHandler<SearchInputs> = useCallback(async (data) => {
    setLoading(true);
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/packages?q=${data.searchTerm}`,
    );
    if (response.ok) {
      setError(null);
      setPackages(await response.json());
    } else {
      setError(`Error ${response.status}: ${response.statusText}`);
      setPackages(null);
    }
    setLoading(false);
  }, []);

  return (
    <div className="mx-16">
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
      {loading && <Spinner />}
      {(packages && (
        <div>
          {packages.map((pkg: Package) => (
            <div>
              {pkg.name} <em>({pkg.downloads_total} downloads)</em>
            </div>
          ))}
        </div>
      )) || <div className="mt-8">Try entering a search term above.</div>}
      {error && <Toast>{error}</Toast>}
    </div>
  );
}
