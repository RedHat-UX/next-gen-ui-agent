import { List, ListItem, ListComponent } from "@patternfly/react-core";

type ListWrapperProps = {
  variant?: keyof typeof ListComponent;
  items: (string | { label: string; subItems?: string[] })[];
};

export default function ListWrapper({
  variant = "ul",
  items,
}: ListWrapperProps) {
  return (
    <List component={ListComponent[variant]}>
      {items.map((item, index) =>
        typeof item === "string" ? (
          <ListItem key={index}>{item}</ListItem>
        ) : (
          <ListItem key={index}>
            {item.label}
            {item.subItems && (
              <List component={ListComponent.ul}>
                {item.subItems.map((subItem, subIndex) => (
                  <ListItem key={subIndex}>{subItem}</ListItem>
                ))}
              </List>
            )}
          </ListItem>
        )
      )}
    </List>
  );
}
