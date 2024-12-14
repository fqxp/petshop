import { use } from "react";
import { Package } from "./types";
type Props = {
  packagesPromise: Promise<Package[]>;
};

export default function PackageList({ packagesPromise }: Props) {
  const packages = use(packagesPromise);

  return (
    <ul>
      {packages.map((pkg: Package) => (
        <li key={pkg.id}>
          {pkg.name} <em>({pkg.downloads_total} downloads)</em>
        </li>
      ))}
    </ul>
  );
}
