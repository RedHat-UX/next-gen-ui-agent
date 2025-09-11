import { Card, CardBody, CardHeader, CardTitle } from "@patternfly/react-core";
import React from "react";

interface ImageComponentProps {
  component: "image";
  id: string;
  image?: string | null;
  title: string;
  className?: string;
}

const ImageComponent: React.FC<ImageComponentProps> = ({
  id,
  image,
  title,
  className,
}) => {
  return (
    <Card id={id} className={className} style={{ maxWidth: "400px" }}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardBody>
        {image ? (
          <img
            src={image}
            alt={title}
            style={{
              width: "100%",
              height: "auto",
              borderRadius: "var(--pf-global--BorderRadius--sm)",
              objectFit: "cover",
            }}
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
              target.parentElement!.innerHTML = `<p style="color: var(--pf-global--Color--200); text-align: center; padding: 20px;">Image failed to load</p>`;
            }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "200px",
              backgroundColor: "var(--pf-global--Color--200)",
              borderRadius: "var(--pf-global--BorderRadius--sm)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--pf-global--Color--300)",
            }}
          >
            No image provided
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default ImageComponent;
