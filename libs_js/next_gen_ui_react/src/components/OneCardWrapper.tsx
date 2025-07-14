import {
  DescriptionList,
  DescriptionListTerm,
  DescriptionListGroup,
  DescriptionListDescription,
  Card,
  CardBody,
  Divider,
  Flex,
  FlexItem,
  Title,
} from "@patternfly/react-core";
import React from "react";

interface DataField {
  name: string;
  data_path: string;
  data: (string | number | boolean | null)[];
}

interface OneCardProps {
  title: string;
  fields: DataField[];
  image?: string | null;
  id?: string;
  imageSize?: "sm" | "md" | "lg";
  className?: string;
}

const OneCardWrapper: React.FC<OneCardProps> = ({
  title,
  fields,
  image,
  id,
  imageSize = "md",
  className,
}) => {
  const getImageFlexBasis = () => {
    switch (imageSize) {
      case "sm":
        return "15%";
      case "lg":
        return "25%";
      default:
        return "20%";
    }
  };

  return (
    <Card 
      id={id} 
      className={className}
      style={{ 
        maxWidth: "1440px", 
        margin: "0 auto",
        width: "100%"
      }}
    >
      <CardBody>
        <Flex spaceItems={{ default: "spaceItemsLg" }} alignItems={{ default: "alignItemsFlexStart" }}>
          {/* Left Column - Image */}
          {image && (
            <FlexItem shrink={{ default: "shrink" }} style={{ flexBasis: getImageFlexBasis() }}>
              <img
                src={image}
                alt={title}
                style={{
                  width: "100%",
                  height: "auto",
                  borderRadius: "var(--pf-global--BorderRadius--sm)",
                  objectFit: "cover",
                }}
              />
            </FlexItem>
          )}

          {/* Right Column - Title + Fields */}
          <FlexItem grow={{ default: "grow" }}>
            <Title headingLevel="h4" size="lg" style={{ marginBottom: "16px" }}>
              {title}
            </Title>
            <Divider component="div" style={{ marginTop: "16px", marginBottom: "16px" }} />
            <div>
              <DescriptionList isAutoFit>
                {fields?.map((field, idx) => (
                  <DescriptionListGroup key={idx}>
                    <DescriptionListTerm>{field.name}</DescriptionListTerm>
                    <DescriptionListDescription>
                      {field.data.map((item) =>
                        item === null ? "N/A" : String(item)
                      ).join(", ")}
                    </DescriptionListDescription>
                  </DescriptionListGroup>
                ))}
              </DescriptionList>
            </div>
          </FlexItem>
        </Flex>
      </CardBody>
    </Card>
  );
};

export default OneCardWrapper;
