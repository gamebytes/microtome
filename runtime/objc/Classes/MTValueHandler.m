//
// microtome - Copyright 2012 Three Rings Design

#import "MTValueHandler.h"

#import "MTPage.h"
#import "MTPageRef.h"
#import "MTTome.h"
#import "MTLibrary.h"
#import "MTType.h"
#import "MTProp.h"

@implementation MTValueHandlerBase

- (Class)valueType {
    OOO_IS_ABSTRACT();
    return nil;
}

- (BOOL)handlesSubclasses {
    OOO_IS_ABSTRACT();
    return NO;
}

- (void)withLibrary:(MTLibrary*)library type:(MTType*)type resolveRefs:(id)value {
    // do nothing by default
}

- (void)validatePropValue:(MTObjectProp*)prop {
    if (!prop.nullable && prop.value == nil) {
        [NSException raise:NSGenericException format:@"nil value for non-nullable prop [name=%@]", prop.name];
    }
    if (prop.value != nil && ![prop.value isKindOfClass:self.valueType]) {
        [NSException raise:NSGenericException
                    format:@"incompatible value type [name=%@, requiredType=%@, actualType=%@]",
                        prop.name, NSStringFromClass(self.valueType),
                        NSStringFromClass([prop.value class])];
    }
}

@end

// Built-in value handlers

@implementation MTStringValueHandler

- (Class)valueType { return [NSString class]; }
- (BOOL)handlesSubclasses { return NO; }

@end

@implementation MTListValueHandler

- (Class)valueType { return [NSArray class]; }
- (BOOL)handlesSubclasses { return NO; }

- (void)withLibrary:(MTLibrary*)library type:(MTType*)type resolveRefs:(id)value {
    NSArray* list = (NSArray*)value;
    id<MTValueHandler> childHandler = [library requireValueHandlerForClass:type.subtype.clazz];
    for (id child in list) {
        [childHandler withLibrary:library type:type.subtype resolveRefs:child];
    }
}

@end

@implementation MTPageValueHandler

- (Class)valueType { return [MTMutablePage class]; }
- (BOOL)handlesSubclasses { return YES; }

- (void)withLibrary:(MTLibrary*)library type:(MTType*)type resolveRefs:(id)value {
    MTMutablePage* page = (MTMutablePage*)value;
    for (MTProp* prop in page.props) {
        if ([prop isKindOfClass:[MTObjectProp class]]) {
            MTObjectProp* objectProp = (MTObjectProp*)prop;
            if (objectProp.value != nil) {
                id<MTValueHandler> propHandler = [library requireValueHandlerForClass:objectProp.valueType.clazz];
                [propHandler withLibrary:library type:objectProp.valueType resolveRefs:objectProp.value];
            }
        }
    }
}

@end

@implementation MTPageRefValueHandler

- (Class)valueType { return [MTMutablePageRef class]; }
- (BOOL)handlesSubclasses { return NO; }

- (void)withLibrary:(MTLibrary*)library type:(MTType*)type resolveRefs:(id)value {
    MTMutablePageRef* ref = (MTMutablePageRef*)value;
    ref.page = [library requirePage:ref.pageName pageClass:ref.pageType];
}

@end

@implementation MTTomeValueHandler

- (Class)valueType { return [MTMutableTome class]; }
- (BOOL)handlesSubclasses { return NO; }

- (void)withLibrary:(MTLibrary*)library type:(MTType*)type resolveRefs:(id)value {
    MTMutableTome* tome = (MTMutableTome*)value;
    id<MTValueHandler> pageHandler = [library requireValueHandlerForClass:tome.pageType];
    for (id<MTPage> page in tome.pages) {
        [pageHandler withLibrary:library type:type.subtype resolveRefs:page];
    }
}

@end