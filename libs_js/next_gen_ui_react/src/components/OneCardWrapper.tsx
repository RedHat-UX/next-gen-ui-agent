import {
  DescriptionList,
  DescriptionListTerm,
  DescriptionListGroup,
  DescriptionListDescription,
  Card,
  CardHeader,
  Title,
  CardBody,
  Divider,
} from "@patternfly/react-core";
import React from "react";

interface DataField {
  name: string;
  data_path: string;
  data: (string | number | null)[];
}

interface OneCardProps {
  title: string;
  fields: DataField[];
  field_names: string[];
  data_length: number;
  image?: string | null;
}

const OneCardWrapper: React.FC<{ config: OneCardProps }> = ({ config }) => {
  console.log(config);
  return (
    <Card>
      <CardHeader>
        {/* {config.image && <Brand src={config.image} alt={config.title} />} */}
        <Title headingLevel="h4" size="lg">
          {config.title}
        </Title>
      </CardHeader>
      <Divider />
      <CardBody>
        <DescriptionList isAutoFit>
          {config.fields.map((field, idx) => (
            <DescriptionListGroup key={idx}>
              <DescriptionListTerm>{field.name}</DescriptionListTerm>
              <DescriptionListDescription>
                {field.data.join(", ")}
              </DescriptionListDescription>
            </DescriptionListGroup>
          ))}
        </DescriptionList>
      </CardBody>
    </Card>
  );
};

export default OneCardWrapper;
